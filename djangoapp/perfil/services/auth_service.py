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
from djangoapp.perfil.models import Perfil
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


@transaction.atomic
def start_signup(*, request, email: str, password: str) -> SignupStartResult:
    email_norm = _normalize_email(email)

    existing = User.objects.filter(email__iexact=email_norm).first()
    if existing and existing.is_active:
        raise DomainError(
            code=ErrorCode.AUTH_USER_EXISTS,
            message=get_error_message(ErrorCode.AUTH_USER_EXISTS),
            http_status=400,
        )

    if existing is None:
        user = User(username=email_norm, email=email_norm, is_active=False)
        user.set_password(password)
        user.save()
    else:
        user = existing
        user.is_active = False
        user.set_password(password)
        user.save(update_fields=["is_active", "password"])

    _ensure_profile(user)

    created: CreatedCode = create_code(
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


@transaction.atomic
def verify_signup(*, email: str, code: str) -> SignupVerifyResult:
    email_norm = _normalize_email(email)

    verify_code(email=email_norm, purpose=PURPOSE_SIGNUP, code=code, consume=True)

    user = User.objects.filter(email__iexact=email_norm).first()
    if not user:
        raise DomainError(
            code=ErrorCode.AUTH_USER_NOT_FOUND,
            message=get_error_message(ErrorCode.AUTH_USER_NOT_FOUND),
            http_status=404,
        )

    user.is_active = True
    user.save(update_fields=["is_active"])

    _safe_send_signup_verified_email(email=email_norm)

    return SignupVerifyResult(user=user, email=email_norm)


@transaction.atomic
def resend_signup_code(*, request, email: str) -> SignupStartResult:
    email_norm = _normalize_email(email)

    user = User.objects.filter(email__iexact=email_norm).first()
    if not user:
        raise DomainError(
            code=ErrorCode.AUTH_USER_NOT_FOUND,
            message=get_error_message(ErrorCode.AUTH_USER_NOT_FOUND),
            http_status=404,
        )

    if user.is_active:
        raise DomainError(
            code=ErrorCode.AUTH_ALREADY_ACTIVE,
            message=get_error_message(ErrorCode.AUTH_ALREADY_ACTIVE),
            http_status=400,
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