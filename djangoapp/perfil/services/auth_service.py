""" Este módulo contém os serviços para o login e registo do utilizador. """
# djangoapp/perfil/services/auth_service.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction

from djangoapp.perfil.error_messages import get_error_message
from djangoapp.perfil.errors import DomainError, ErrorCode
from djangoapp.perfil.models import PendingSignup, Perfil
from djangoapp.perfil.services.email_service import (
    send_signup_code_email,
    send_signup_verified_email,
)
from djangoapp.perfil.services.verification_code_service import (
    CreatedCode,
    create_code,
    resend_code,
    verify_code,
)

logger = logging.getLogger(__name__)
User = get_user_model()

PURPOSE_SIGNUP = "signup"

# TODO: create a management command to clean up PendingSignup with more than X days and used_at is null
@dataclass(frozen=True)
class SignupStartResult:
    email: str
    expires_at: datetime
    resend_count: int


@dataclass(frozen=True)
class SignupVerifyResult:
    user: AbstractBaseUser
    email: str


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _ensure_profile(user: AbstractBaseUser) -> Perfil:
    # English comment: Perfil expects a concrete User instance; AbstractBaseUser is fine at runtime.
    perfil, _ = Perfil.objects.get_or_create(usuario=user)
    return perfil


def _safe_send_signup_code_email(*, email: str, code: str) -> None:
    try:
        send_signup_code_email(email=email, code=code)
    except Exception:
        logger.exception("Failed to send signup verification email", extra={"email": email})


def _safe_send_signup_verified_email(*, email: str) -> None:
    try:
        send_signup_verified_email(email=email)
    except Exception:
        logger.exception("Failed to send signup verified email", extra={"email": email})



def start_signup(*, request, email: str, password: str) -> SignupStartResult:
    email_norm = _normalize_email(email)

    with transaction.atomic():
        existing = User.objects.select_for_update().filter(email__iexact=email_norm).first()
        if existing and getattr(existing, "is_active", False):
            raise DomainError(
                code=ErrorCode.AUTH_USER_EXISTS,
                message=get_error_message(ErrorCode.AUTH_USER_EXISTS),
                http_status=400,
            )

        pending = PendingSignup.objects.select_for_update().filter(email=email_norm).first()
        if pending is None:
            pending = PendingSignup(email=email_norm)
        else:
            # English comment: PendingSignup is not source of truth; allow restarting signup anytime.
            if pending.is_used:
                pending.used_at = None

        pending.set_temp_password(password)
        pending.ip_address = request.META.get("REMOTE_ADDR")
        pending.user_agent = request.META.get("HTTP_USER_AGENT")
        pending.save()

        created: CreatedCode = create_code(
            request=request,
            email=email_norm,
            purpose=PURPOSE_SIGNUP,
        )

    # English comment: external IO outside transaction
    _safe_send_signup_code_email(email=email_norm, code=created.raw_code)

    return SignupStartResult(
        email=email_norm,
        expires_at=created.expires_at,
        resend_count=created.resend_count,
    )

def verify_signup(*, email: str, code: str) -> SignupVerifyResult:
    email_norm = _normalize_email(email)

    # Phase A (no outer transaction): validate + consume code
    # English comment: This must run outside outer atomic so attempts are persisted on failures.
    verify_code(email=email_norm, purpose=PURPOSE_SIGNUP, code=code, consume=True)

    # Phase B (atomic): apply state changes
    with transaction.atomic():
        pending = PendingSignup.objects.select_for_update().filter(email=email_norm).first()
        if not pending or pending.is_used:
            # TODO: Add a new code to the error_messages.py
            raise DomainError(
                code=ErrorCode.AUTH_USER_NOT_FOUND,
                message="Sessão de registo expirada. Faz signup novamente.",
                http_status=404,
            )

        user = User.objects.filter(email__iexact=email_norm).first()

        if user is None:
            user = User(username=email_norm, email=email_norm, is_active=True)
            user.password = pending.password_hash
            user.save()
            _ensure_profile(user)
        else:
            if getattr(user, "is_active", False):
                raise DomainError(
                    code=ErrorCode.AUTH_ALREADY_ACTIVE,
                    message=get_error_message(ErrorCode.AUTH_ALREADY_ACTIVE),
                    http_status=400,
                )

            user.is_active = True
            user.password = pending.password_hash
            user.save(update_fields=["is_active", "password"])
            _ensure_profile(user)

        pending.mark_used()

    _safe_send_signup_verified_email(email=email_norm)
    return SignupVerifyResult(user=user, email=email_norm)

def resend_signup_code(*, request, email: str) -> SignupStartResult:
    email_norm = _normalize_email(email)

    if User.objects.filter(email__iexact=email_norm, is_active=True).exists():
        raise DomainError(
            code=ErrorCode.AUTH_ALREADY_ACTIVE,
            message=get_error_message(ErrorCode.AUTH_ALREADY_ACTIVE),
            http_status=400,
        )

    with transaction.atomic():
        pending = PendingSignup.objects.select_for_update().filter(email=email_norm).first()
        if not pending or pending.is_used:
            # TODO: Add a new code to the error_messages.py
            raise DomainError(
                code=ErrorCode.AUTH_USER_NOT_FOUND,
                message="Sessão de registo expirada. Faz signup novamente.",
                http_status=404,
            )

        created: CreatedCode = resend_code(
            request=request,
            email=email_norm,
            purpose=PURPOSE_SIGNUP,
        )

    _safe_send_signup_code_email(email=email_norm, code=created.raw_code)

    return SignupStartResult(
        email=email_norm,
        expires_at=created.expires_at,
        resend_count=created.resend_count,
    )