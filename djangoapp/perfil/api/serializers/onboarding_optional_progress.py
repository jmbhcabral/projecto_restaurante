# djangoapp/perfil/api/serializers/onboarding_optional_progress.py
from __future__ import annotations

from typing import Any

from rest_framework import serializers

from djangoapp.perfil.models import Perfil


class OnboardingOptionalProgressSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    telemovel = serializers.CharField(required=False, allow_blank=True, max_length=9)
    data_nascimento = serializers.DateField(required=False)

    def validate_telemovel(self, value: str) -> str:
        # English comment: validate only if provided and non-empty
        t = (value or "").strip()
        if not t:
            return ""
        if len(t) != 9 or not t.isdigit():
            raise serializers.ValidationError("O telemóvel tem de ter 9 dígitos.")
        return t

    def save(self, **kwargs: Any) -> Perfil:
        # English comment: expect perfil passed explicitly
        perfil = kwargs.get("perfil")
        if perfil is None or not isinstance(perfil, Perfil):
            raise TypeError("Missing required kwarg: perfil")

        user = perfil.usuario
        data = self.validated_data

        user_update_fields: list[str] = []
        perfil_update_fields: list[str] = []

        if "first_name" in data:
            user.first_name = (data.get("first_name") or "").strip()
            user_update_fields.append("first_name")

        if "last_name" in data:
            user.last_name = (data.get("last_name") or "").strip()
            user_update_fields.append("last_name")

        if "telemovel" in data:
            perfil.telemovel = (data.get("telemovel") or "").strip()
            perfil_update_fields.append("telemovel")

        if "data_nascimento" in data:
            perfil.data_nascimento = data.get("data_nascimento")
            perfil_update_fields.append("data_nascimento")

        # English comment: validate and save only changed models
        if user_update_fields:
            user.full_clean()
            user.save(update_fields=user_update_fields)

        if perfil_update_fields:
            perfil.full_clean()
            perfil.save(update_fields=perfil_update_fields)

        return perfil