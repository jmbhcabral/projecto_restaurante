""" Serializers for password reset. """
# djangoapp/perfil/api/serializers/password_reset.py
from __future__ import annotations

from typing import Any

from rest_framework import serializers

from djangoapp.perfil.services.password_reset_service import (
    PasswordResetStartResult,
    PasswordResetVerifyResult,
    resend_password_reset_code,
    start_password_reset,
    verify_password_reset,
)


class PasswordResetStartSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def save(self, **kwargs: Any) -> PasswordResetStartResult:
        request = self.context.get("request")
        if request is None:
            raise TypeError("Missing request in serializer context")

        return start_password_reset(request=request, email=self.validated_data["email"])


class PasswordResetResendSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def save(self, **kwargs: Any) -> PasswordResetStartResult:
        request = self.context.get("request")
        if request is None:
            raise TypeError("Missing request in serializer context")

        return resend_password_reset_code(request=request, email=self.validated_data["email"])


class PasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6, trim_whitespace=True)
    new_password = serializers.CharField(min_length=8, max_length=128, trim_whitespace=False)

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_code(self, value: str) -> str:
        # normalize code input.
        return value.strip()

    def save(self, **kwargs: Any) -> PasswordResetVerifyResult:
        return verify_password_reset(
            email=self.validated_data["email"],
            code=self.validated_data["code"],
            new_password=self.validated_data["new_password"],
        )