""" Este módulo contém os serviços para a redefinição de senha. """
# djangoapp/perfil/services/password_reset_service.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from djangoapp.perfil.constants import PASSWORD_RESET_PURPOSE
from djangoapp.perfil.errors import CommonErrorCode, DomainError
from djangoapp.perfil.services.email_service import send_password_reset_code_email
from djangoapp.perfil.services.verification_code_service import (
    CreatedCode,
    create_code,
    resend_code,
    verify_code,
)

User = get_user_model()

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class PasswordResetStartResult:
    email: str
    expires_at: Optional[datetime]
    resend_count: Optional[int]


@dataclass(frozen=True)
class PasswordResetVerifyResult:
    email: str


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _safe_send_password_reset_code_email(*, email: str, code: str) -> None:
    try:
        send_password_reset_code_email(email=email, code=code)
    except Exception:
        logger.exception("Failed to send password reset email", extra={"email": email})


@transaction.atomic
def start_password_reset(*, request, email: str) -> PasswordResetStartResult:
    email_norm = _normalize_email(email)

    user = User.objects.filter(email__iexact=email_norm, is_active=True).first()

    # anti-enumeration: if user doesn't exist, return a neutral success.
    if not user:
        return PasswordResetStartResult(email=email_norm, expires_at=None, resend_count=None)

    created: CreatedCode = create_code(
        request=request,
        email=email_norm,
        purpose=PASSWORD_RESET_PURPOSE,
    )

    _safe_send_password_reset_code_email(email=email_norm, code=created.raw_code)

    return PasswordResetStartResult(
        email=email_norm,
        expires_at=created.expires_at,
        resend_count=created.resend_count,
    )


@transaction.atomic
def resend_password_reset_code(*, request, email: str) -> PasswordResetStartResult:
    email_norm = _normalize_email(email)

    user = User.objects.filter(email__iexact=email_norm, is_active=True).first()

    # anti-enumeration: behave like success even if user doesn't exist.
    if not user:
        return PasswordResetStartResult(email=email_norm, expires_at=None, resend_count=None)

    created: CreatedCode = resend_code(
        request=request,
        email=email_norm,
        purpose=PASSWORD_RESET_PURPOSE,
    )

    _safe_send_password_reset_code_email(email=email_norm, code=created.raw_code)

    return PasswordResetStartResult(
        email=email_norm,
        expires_at=created.expires_at,
        resend_count=created.resend_count,
    )


@transaction.atomic
def verify_password_reset(*, email: str, code: str, new_password: str) -> PasswordResetVerifyResult:
    email_norm = _normalize_email(email)

    # validate password with Django validators.
    try:
        validate_password(new_password)
    except DjangoValidationError as e:
        raise DomainError(
            code=CommonErrorCode.BAD_REQUEST,
            message=e.messages[0],
            http_status=400,
        )


    user = User.objects.filter(email__iexact=email_norm, is_active=True).first()
    if not user:
        # if user is missing here, treat as generic failure.
        raise DomainError(
            code=CommonErrorCode.BAD_REQUEST,
            message="Pedido inválido.",
            http_status=400,
        )

    verify_code(
        email=email_norm,
        purpose=PASSWORD_RESET_PURPOSE,
        code=code,
        consume=True,
    )

    user.set_password(new_password)
    user.save(update_fields=["password"])

    return PasswordResetVerifyResult(email=email_norm)