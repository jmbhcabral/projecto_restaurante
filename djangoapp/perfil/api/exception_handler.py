""" Este módulo contém o handler de exceções para o aplicativo de perfil. """
# djangoapp/perfil/api/exception_handler.py
from __future__ import annotations

import logging
from typing import Any

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    Throttled,
    UnsupportedMediaType,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from djangoapp.perfil.errors import CommonErrorCode, DomainError

logger = logging.getLogger(__name__)


# English comment: map DRF exceptions to stable error codes
DRF_CODE_MAP: dict[type[Exception], str] = {
    NotAuthenticated: CommonErrorCode.AUTH_NOT_AUTHENTICATED,
    AuthenticationFailed: CommonErrorCode.AUTH_FAILED,
    PermissionDenied: CommonErrorCode.AUTH_FORBIDDEN,
    Throttled: CommonErrorCode.RATE_LIMITED,
    NotFound: CommonErrorCode.NOT_FOUND,
    MethodNotAllowed: CommonErrorCode.METHOD_NOT_ALLOWED,
    ParseError: CommonErrorCode.BAD_REQUEST,
    UnsupportedMediaType: CommonErrorCode.UNSUPPORTED_MEDIA_TYPE,
}


def _error_response(*, code: str, message: str, http_status: int, field: str | None = None) -> Response:
    # English comment: consistent error shape + optional field for UI
    payload: dict[str, Any] = {"code": code, "message": message}
    if field:
        payload["field"] = field
    return Response({"error": payload}, status=http_status)


def _extract_validation_error(detail: Any) -> tuple[str, str | None]:
    """
    English comment: Returns (message, field).
    For field-level errors, returns the first field and its first error message.
    """
    if isinstance(detail, dict) and detail:
        field = next(iter(detail.keys()))
        first_val = detail[field]

        if isinstance(first_val, list) and first_val:
            return str(first_val[0]), str(field)

        return str(first_val), str(field)

    if isinstance(detail, list) and detail:
        return str(detail[0]), None

    if isinstance(detail, str):
        return detail, None

    return "Dados inválidos.", None


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """
    Level-10 exception handler:
    - DomainError => stable code + message + status
    - DRF known exceptions => mapped code + clean message
    - ValidationError => VALIDATION_ERROR + message + field
    - Http404 => NOT_FOUND
    - Other APIException => DRF_ERROR + detail (normalized)
    - Unknown => INTERNAL_ERROR
    """
    # 1) Domain errors (business rules)
    if isinstance(exc, DomainError):
        return _error_response(code=exc.code, message=exc.message, http_status=exc.http_status)

    # 2) Django 404 (outside DRF)
    if isinstance(exc, Http404):
        return _error_response(
            code=CommonErrorCode.NOT_FOUND,
            message="Recurso não encontrado.",
            http_status=status.HTTP_404_NOT_FOUND,
        )

    # 3) DRF validation errors (with field)
    if isinstance(exc, ValidationError):
        detail = getattr(exc, "detail", None)
        message, field = _extract_validation_error(detail)
        return _error_response(
            code=CommonErrorCode.VALIDATION_ERROR,
            message=message,
            http_status=status.HTTP_400_BAD_REQUEST,
            field=field,
        )

    # 4) DRF mapped exceptions
    for exc_type, mapped_code in DRF_CODE_MAP.items():
        if isinstance(exc, exc_type):
            detail = getattr(exc, "detail", None)
            message = str(detail) if detail else "Erro."
            http_status = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)
            return _error_response(code=mapped_code, message=message, http_status=http_status)

    # 5) Let DRF handle other APIExceptions, then normalize its response
    response = drf_exception_handler(exc, context)
    if response is not None:
        http_status = response.status_code
        code = "DRF_ERROR"
        field_name: str | None = None
        message = "Erro."

        if isinstance(exc, APIException):
            default_code = getattr(exc, "default_code", None)
            if default_code:
                code = f"DRF_{str(default_code).upper()}"

        if isinstance(response.data, dict):
            if "detail" in response.data:
                message = str(response.data["detail"])
            else:
                extracted_message, extracted_field = _extract_validation_error(response.data)
                message = extracted_message
                field_name = extracted_field
        elif isinstance(response.data, list) and response.data:
            message = str(response.data[0])

        return _error_response(code=code, message=message, http_status=http_status, field=field_name)

    # 6) Unknown exception
    logger.exception("Unhandled exception", exc_info=exc)
    return _error_response(
        code=CommonErrorCode.INTERNAL_ERROR,
        message="Erro interno. Tenta novamente.",
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )