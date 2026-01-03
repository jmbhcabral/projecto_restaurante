""" Este módulo contém os serviços para os códigos de verificação do utilizador. """
# djangoapp/perfil/services/verification_code_service.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from django.db import transaction
from django.utils import timezone

from djangoapp.perfil.error_messages import get_error_message
from djangoapp.perfil.errors import DomainError, ErrorCode
from djangoapp.perfil.models import VerificationCode
from djangoapp.perfil.services.codes import (
    generate_verification_code,
    make_code_digest,
    safe_compare_digest,
)

DEFAULT_TTL_MINUTES = 10
DEFAULT_CODE_LENGTH = 6
MAX_ATTEMPTS = 5
MAX_RESENDS = 5


@dataclass(frozen=True)
class CreatedCode:
    # English comment: raw_code is returned only to be sent via email/SMS
    raw_code: str
    expires_at: datetime
    resend_count: int


def _now():
    return timezone.now()


def _get_client_ip(request) -> Optional[str]:
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _get_user_agent(request) -> Optional[str]:
    if request is None:
        return None
    return request.META.get("HTTP_USER_AGENT")


def _get_last_resend_count(*, email: str, purpose: str) -> int:
    last = (
        VerificationCode.objects
        .filter(email=email, purpose=purpose)
        .order_by("-created_at")
        .first()
    )
    return last.resend_count if last else 0


@transaction.atomic
def invalidate_open_codes(*, email: str, purpose: str) -> int:
    # English comment: marks any open code as used so only the newest can be valid
    email_norm = email.strip().lower()
    now = _now()
    qs = VerificationCode.objects.filter(email=email_norm, purpose=purpose, used_at__isnull=True)
    return qs.update(used_at=now, updated_at=now)


@transaction.atomic
def create_code(
    *,
    request,
    email: str,
    purpose: str,
    ttl_minutes: int = DEFAULT_TTL_MINUTES,
    length: int = DEFAULT_CODE_LENGTH,
) -> CreatedCode:
    email_norm = email.strip().lower()

    last_resends = _get_last_resend_count(email=email_norm, purpose=purpose)
    if last_resends >= MAX_RESENDS:
        raise DomainError(
            code=ErrorCode.CODE_MAX_RESENDS,
            message=get_error_message(ErrorCode.CODE_MAX_RESENDS),
            http_status=429,
        )

    invalidate_open_codes(email=email_norm, purpose=purpose)

    raw_code = generate_verification_code(length=length)
    digest = make_code_digest(email=email_norm, purpose=purpose, code=raw_code)
    expires_at = _now() + timedelta(minutes=ttl_minutes)

    vc_resend_count = 0

    VerificationCode.objects.create(
        email=email_norm,
        purpose=purpose,
        code_digest=digest,
        expires_at=expires_at,
        resend_count=vc_resend_count,
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
    )

    return CreatedCode(raw_code=raw_code, expires_at=expires_at, resend_count=vc_resend_count)


@transaction.atomic
def resend_code(
    *,
    request,
    email: str,
    purpose: str,
    ttl_minutes: int = DEFAULT_TTL_MINUTES,
    length: int = DEFAULT_CODE_LENGTH,
) -> CreatedCode:
    email_norm = email.strip().lower()

    last_resends = _get_last_resend_count(email=email_norm, purpose=purpose)
    if last_resends >= MAX_RESENDS:
        raise DomainError(
            code=ErrorCode.CODE_MAX_RESENDS,
            message=get_error_message(ErrorCode.CODE_MAX_RESENDS),
            http_status=429,
        )

    invalidate_open_codes(email=email_norm, purpose=purpose)

    raw_code = generate_verification_code(length=length)
    digest = make_code_digest(email=email_norm, purpose=purpose, code=raw_code)
    expires_at = _now() + timedelta(minutes=ttl_minutes)

    vc_resend_count = last_resends + 1

    VerificationCode.objects.create(
        email=email_norm,
        purpose=purpose,
        code_digest=digest,
        expires_at=expires_at,
        resend_count=vc_resend_count,
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
    )

    return CreatedCode(raw_code=raw_code, expires_at=expires_at, resend_count=vc_resend_count)


@transaction.atomic
def verify_code(
    *,
    email: str,
    purpose: str,
    code: str,
    consume: bool = True,
) -> bool:
    email_norm = email.strip().lower()
    code_norm = code.strip()

    latest = (
        VerificationCode.objects
        .filter(email=email_norm, purpose=purpose)
        .order_by("-created_at")
        .first()
    )

    if not latest:
        raise DomainError(
            code=ErrorCode.CODE_NOT_FOUND,
            message=get_error_message(ErrorCode.CODE_NOT_FOUND),
            http_status=400,
        )

    if latest.used_at is not None:
        raise DomainError(
            code=ErrorCode.CODE_INVALIDATED,
            message=get_error_message(ErrorCode.CODE_INVALIDATED),
            http_status=400,
        )

    if latest.expires_at and _now() > latest.expires_at:
        raise DomainError(
            code=ErrorCode.CODE_EXPIRED,
            message=get_error_message(ErrorCode.CODE_EXPIRED),
            http_status=400,
        )

    if latest.attempts >= MAX_ATTEMPTS:
        raise DomainError(
            code=ErrorCode.CODE_MAX_ATTEMPTS,
            message=get_error_message(ErrorCode.CODE_MAX_ATTEMPTS),
            http_status=429,
        )

    received = make_code_digest(email=email_norm, purpose=purpose, code=code_norm)

    # English comment: always increment attempts to keep behavior consistent
    latest.attempts += 1
    latest.updated_at = _now()

    if not safe_compare_digest(latest.code_digest, received):
        latest.save(update_fields=["attempts", "updated_at"])
        raise DomainError(
            code=ErrorCode.CODE_INCORRECT,
            message=get_error_message(ErrorCode.CODE_INCORRECT),
            http_status=400,
        )

    if consume:
        latest.used_at = _now()
        latest.updated_at = _now()
        latest.save(update_fields=["attempts", "used_at", "updated_at"])
    else:
        latest.save(update_fields=["attempts", "updated_at"])

    return True