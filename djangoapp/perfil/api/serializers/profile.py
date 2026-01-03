""" Este módulo contém os serializers para o perfil do utilizador. """
# djangoapp/perfil/api/serializers/profile.py
from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from djangoapp.perfil.models import Perfil
from djangoapp.utils.model_validators import validar_nif

User = get_user_model()


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name")
        read_only_fields = ("id", "email", "username")


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = (
            "data_nascimento",
            "telemovel",
            "nif",
            "onboarding_min_completed",
            "phone_verified",
            "has_valid_nif",
            "has_delivery_address",
            "has_billing_address",
            "notificacoes_email",
            "notificacoes_telemovel",
        )
        read_only_fields = (
            "onboarding_min_completed",
            "phone_verified",
            "has_valid_nif",
            "has_delivery_address",
            "has_billing_address",
        )

    def validate_nif(self, value: str) -> str:
        # English comments per your preference
        if not value:
            return value
        v = value.strip()
        if len(v) != 9 or not v.isdigit():
            raise serializers.ValidationError("O NIF tem de ter 9 dígitos.")
        if not validar_nif(v):
            raise serializers.ValidationError("NIF inválido.")
        return v

    def validate_telemovel(self, value: str) -> str:
        if not value:
            return value
        v = value.strip()
        if len(v) != 9 or not v.isdigit():
            raise serializers.ValidationError("O telemóvel tem de ter 9 dígitos.")
        return v

    def update(self, instance: Perfil, validated_data: dict[str, Any]) -> Perfil:
        # Keep derived flags consistent
        instance = super().update(instance, validated_data)

        # Derived flags: keep them in sync
        instance.has_valid_nif = bool(instance.nif and validar_nif(instance.nif))
        instance.save(update_fields=["has_valid_nif", "updated_at"])
        return instance