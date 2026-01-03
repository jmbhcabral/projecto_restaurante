"""
Serializers for authentication (new flow).
- Login
- Signup start
- Signup verify
- Signup resend
"""

from __future__ import annotations

from typing import Any, cast

from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from djangoapp.perfil.error_messages import get_error_message
from djangoapp.perfil.errors import DomainError, ErrorCode
from djangoapp.perfil.services.auth_service import (
    SignupStartResult,
    SignupVerifyResult,
    resend_signup_code,
    start_signup,
    verify_signup,
)

# =====================================================
# LOGIN
# =====================================================


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        request = self.context.get("request")
        identifier = attrs["identifier"].strip()
        password = attrs["password"]

        user = authenticate(request, username=identifier, password=password)
        if user is None:
            user = authenticate(request, identifier=identifier, password=password)

        if user is None:
            raise DomainError(
                code=ErrorCode.AUTH_INVALID_CREDENTIALS,
                message=get_error_message(ErrorCode.AUTH_INVALID_CREDENTIALS),
                http_status=400,
            )

        if not getattr(user, "is_active", True):
            raise DomainError(
                code=ErrorCode.AUTH_DISABLED,
                message=get_error_message(ErrorCode.AUTH_DISABLED),
                http_status=403,
            )

        # keep the type stable for callers
        attrs["user"] = cast(AbstractBaseUser, user)
        return attrs


# =====================================================
# SIGNUP – START
# =====================================================


class SignupStartSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value: str) -> str:
        # normalize once at the boundary
        return value.strip().lower()

    def validate_password(self, value: str) -> str:
        try:
            django_validate_password(value)
        except DjangoValidationError as e:
            # keep UX simple: return the first validator message
            raise serializers.ValidationError(e.messages[0])
        return value

    def save(self, **kwargs: Any) -> SignupStartResult:
        """
        Starts the signup process:
        - creates inactive user
        - generates verification code
        - returns metadata (expires_at, resend_count)
        """
        request = self.context.get("request")
        if request is None:
            raise TypeError("Missing request in serializer context")

        return start_signup(
            request=request,
            email=self.validated_data["email"],
            password=self.validated_data["password"],
        )


# =====================================================
# SIGNUP – VERIFY CODE
# =====================================================


class SignupVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, trim_whitespace=True)

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_code(self, value: str) -> str:
        code = value.replace(" ", "").strip()
        if len(code) != 6 or not code.isdigit():
            raise serializers.ValidationError("Código inválido.")
        return code

    def save(self, **kwargs: Any) -> SignupVerifyResult:
        """
        Verifies the signup code and activates the user.
        """
        return verify_signup(
            email=self.validated_data["email"],
            code=self.validated_data["code"],
        )


# =====================================================
# SIGNUP – RESEND CODE
# =====================================================


class SignupResendSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def save(self, **kwargs: Any) -> SignupStartResult:
        """
        Resends the signup verification code.
        """
        request = self.context.get("request")
        if request is None:
            raise TypeError("Missing request in serializer context")

        return resend_signup_code(
            request=request,
            email=self.validated_data["email"],
        )