""" Este módulo contém os erros para o aplicativo de perfil. """
# djangoapp/perfil/errors.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


class ErrorCode:
    """Domain-specific error codes."""

    # Verification codes
    CODE_NOT_FOUND: Final = "CODE_NOT_FOUND"
    CODE_INVALIDATED: Final = "CODE_INVALIDATED"
    CODE_EXPIRED: Final = "CODE_EXPIRED"
    CODE_INCORRECT: Final = "CODE_INCORRECT"
    CODE_MAX_ATTEMPTS: Final = "CODE_MAX_ATTEMPTS"
    CODE_MAX_RESENDS: Final = "CODE_MAX_RESENDS"

    # Rate limiting (domain)
    RATE_LIMITED: Final = "RATE_LIMITED"
    
    # Auth
    AUTH_USER_EXISTS: Final = "AUTH_USER_EXISTS"
    AUTH_USER_NOT_FOUND: Final = "AUTH_USER_NOT_FOUND"
    AUTH_ALREADY_ACTIVE: Final = "AUTH_ALREADY_ACTIVE"
    AUTH_DISABLED: Final = "AUTH_DISABLED"
    AUTH_INVALID_CREDENTIALS: Final = "AUTH_INVALID_CREDENTIALS"

    # Signup flow (temp_user)
    AUTH_SIGNUP_NOT_STARTED: Final = "AUTH_SIGNUP_NOT_STARTED"
    AUTH_SIGNUP_SESSION_EXPIRED: Final = "AUTH_SIGNUP_SESSION_EXPIRED"

class CommonErrorCode:
    """Cross-cutting / infrastructure error codes."""

    NOT_FOUND: Final = "NOT_FOUND"
    METHOD_NOT_ALLOWED: Final = "METHOD_NOT_ALLOWED"

    AUTH_NOT_AUTHENTICATED: Final = "AUTH_NOT_AUTHENTICATED"
    AUTH_FORBIDDEN: Final = "AUTH_FORBIDDEN"
    AUTH_FAILED: Final = "AUTH_FAILED"

    RATE_LIMITED: Final = "RATE_LIMITED"

    BAD_REQUEST: Final = "BAD_REQUEST"
    UNSUPPORTED_MEDIA_TYPE: Final = "UNSUPPORTED_MEDIA_TYPE"

    VALIDATION_ERROR: Final = "VALIDATION_ERROR"
    INTERNAL_ERROR: Final = "INTERNAL_ERROR"


@dataclass(frozen=True)
class DomainError(Exception):
    """
    Domain-level exception that carries a stable code and a user-facing message.
    """
    code: str
    message: str
    http_status: int = 400