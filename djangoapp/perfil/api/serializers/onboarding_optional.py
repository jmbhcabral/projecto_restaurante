# djangoapp/perfil/api/serializers/onboarding_optional.py
from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from djangoapp.perfil.models import Perfil

User = get_user_model()


class OnboardingOptionalSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, allow_blank=False, max_length=150)
    last_name = serializers.CharField(required=True, allow_blank=False, max_length=150)

    telemovel = serializers.CharField(required=True, allow_blank=False, max_length=9)
    data_nascimento = serializers.DateField(required=True)

    def validate_telemovel(self, value: str) -> str:
        # normalize and validate PT phone format (9 digits)
        t = (value or "").strip()
        if len(t) != 9 or not t.isdigit():
            raise serializers.ValidationError("O telemóvel tem de ter 9 dígitos.")
        return t

    def save(self, **kwargs: Any) -> Perfil:
        #  we expect 'perfil' passed explicitly to keep it deterministic
        perfil = kwargs.get("perfil")
        if perfil is None or not isinstance(perfil, Perfil):
            raise TypeError("Missing required kwarg: perfil")

        user = perfil.usuario
        data = self.validated_data

        # 1) Update User fields
        user.first_name = data["first_name"].strip()
        user.last_name = data["last_name"].strip()

        # 2) Update Perfil fields
        perfil.telemovel = data["telemovel"]
        perfil.data_nascimento = data["data_nascimento"]

        # 3) Mark optional onboarding as completed (one-way flag)
        perfil.onboarding_optional_completed = True

        # validate models before persisting
        user.full_clean()
        perfil.full_clean()

        # persist with minimal updates
        user.save(update_fields=["first_name", "last_name"])
        perfil.save(update_fields=["telemovel", "data_nascimento", "onboarding_optional_completed"])

        return perfil