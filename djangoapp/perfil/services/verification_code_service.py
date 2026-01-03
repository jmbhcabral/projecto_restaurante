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

WINDOW_MINUTES = 60

# total sends within window (create + resend) per email+purpose
MAX_SENDS_PER_WINDOW = 6

# per-IP throttle within window (create + resend)
MAX_SENDS_PER_IP_WINDOW = 30

DEFAULT_TTL_MINUTES = 10
DEFAULT_CODE_LENGTH = 6
MAX_ATTEMPTS = 5

# minimum seconds between sends
MIN_SECONDS_BETWEEN_SENDS = 15  # good DX + good security
@dataclass(frozen=True)
class CreatedCode:
    # raw_code is returned only to be sent via email/SMS
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
    cutoff = _now() - timedelta(minutes=WINDOW_MINUTES)
    last = (
        VerificationCode.objects
        .filter(email=email, purpose=purpose, created_at__gte=cutoff)
        .order_by("-created_at")
        .first()
    )
    return last.resend_count if last else 0

def _count_sends_in_window(*, email: str, purpose: str) -> int:
    cutoff = _now() - timedelta(minutes=WINDOW_MINUTES)
    return VerificationCode.objects.filter(
        email=email,
        purpose=purpose,
        created_at__gte=cutoff,
    ).count()


def _count_sends_by_ip_in_window(*, ip: Optional[str], purpose: str) -> int:
    if not ip:
        return 0
    cutoff = _now() - timedelta(minutes=WINDOW_MINUTES)
    return VerificationCode.objects.filter(
        ip_address=ip,
        purpose=purpose,
        created_at__gte=cutoff,
    ).count()
    
def _enforce_rate_limits(*, email: str, purpose: str, request) -> None:
    email_norm = email.strip().lower()
    ip = _get_client_ip(request)

    if _count_sends_in_window(email=email_norm, purpose=purpose) >= MAX_SENDS_PER_WINDOW:
        raise DomainError(
            code=ErrorCode.RATE_LIMITED,
            message=get_error_message(ErrorCode.RATE_LIMITED),
            http_status=429,
        )

    if _count_sends_by_ip_in_window(ip=ip, purpose=purpose) >= MAX_SENDS_PER_IP_WINDOW:
        # IP-based throttle uses same error code to keep contract stable.
        raise DomainError(
            code=ErrorCode.CODE_MAX_RESENDS,
            message=get_error_message(ErrorCode.CODE_MAX_RESENDS),
            http_status=429,
        )

def _has_recent_open_code(*, email: str, purpose: str) -> bool:
    cutoff = _now() - timedelta(seconds=MIN_SECONDS_BETWEEN_SENDS)
    return VerificationCode.objects.filter(
        email=email,
        purpose=purpose,
        used_at__isnull=True,
        created_at__gte=cutoff,
    ).exists()


@transaction.atomic
def invalidate_open_codes(*, email: str, purpose: str) -> int:
    # marks any open code as used so only the newest can be valid
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

    _enforce_rate_limits(email=email_norm, purpose=purpose, request=request)

    if _has_recent_open_code(email=email_norm, purpose=purpose):
        # treat as idempotent send (avoid double click / retries)
        raise DomainError(
            code=ErrorCode.RATE_LIMITED,
            message=get_error_message(ErrorCode.RATE_LIMITED),
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

    _enforce_rate_limits(email=email_norm, purpose=purpose, request=request)

    if _has_recent_open_code(email=email_norm, purpose=purpose):
        # treat as idempotent send (avoid double click / retries)
        raise DomainError(
            code=ErrorCode.RATE_LIMITED,
            message=get_error_message(ErrorCode.RATE_LIMITED),
            http_status=429,
        )

    last_resends = _get_last_resend_count(email=email_norm, purpose=purpose)

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

    latest_open = VerificationCode.objects.filter(
        email=email_norm,
        purpose=purpose,
        used_at__isnull=True,
    ).order_by("-created_at").first()

    if not latest_open:
        raise DomainError(
            code=ErrorCode.CODE_NOT_FOUND,
            message=get_error_message(ErrorCode.CODE_NOT_FOUND),
            http_status=400,
        )

    if latest_open.used_at is not None:
        raise DomainError(
            code=ErrorCode.CODE_INVALIDATED,
            message=get_error_message(ErrorCode.CODE_INVALIDATED),
            http_status=400,
        )

    if latest_open.expires_at and _now() > latest_open.expires_at:
        raise DomainError(
            code=ErrorCode.CODE_EXPIRED,
            message=get_error_message(ErrorCode.CODE_EXPIRED),
            http_status=400,
        )

    if latest_open.attempts >= MAX_ATTEMPTS:
        raise DomainError(
            code=ErrorCode.CODE_MAX_ATTEMPTS,
            message=get_error_message(ErrorCode.CODE_MAX_ATTEMPTS),
            http_status=429,
        )

    received = make_code_digest(email=email_norm, purpose=purpose, code=code_norm)

    # always increment attempts to keep behavior consistent
    latest_open.attempts += 1
    latest_open.updated_at = _now()

    if not safe_compare_digest(latest_open.code_digest, received):
        latest_open.save(update_fields=["attempts", "updated_at"])
        raise DomainError(
            code=ErrorCode.CODE_INCORRECT,
            message=get_error_message(ErrorCode.CODE_INCORRECT),
            http_status=400,
        )

    if consume:
        latest_open.used_at = _now()
        latest_open.updated_at = _now()
        latest_open.save(update_fields=["attempts", "used_at", "updated_at"])
    else:
        latest_open.save(update_fields=["attempts", "updated_at"])

    return True