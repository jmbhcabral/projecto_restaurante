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


class UserMePatchSerializer(serializers.ModelSerializer):
    # English comment: only allow editing names
    class Meta:
        model = User
        fields = ("first_name", "last_name")

    def validate_first_name(self, v: str) -> str:
        return (v or "").strip()

    def validate_last_name(self, v: str) -> str:
        return (v or "").strip()


class PerfilSerializer(serializers.ModelSerializer):
    nif_masked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Perfil
        fields = (
            "data_nascimento",
            "telemovel",
            "nif_masked",          # output only
            "nif",                 # input allowed (we will pop in representation)
            "onboarding_required_completed",
            "onboarding_optional_completed",
            "phone_verified",
            "has_valid_nif",
            "has_delivery_address",
            "has_billing_address",
            "notificacoes_email",
            "notificacoes_telemovel",
            "terms_accepted_at",
            "numero_cliente",
            "tipo_fidelidade_id",
        )
        read_only_fields = (
            "onboarding_required_completed",
            "onboarding_optional_completed",
            "phone_verified",
            "has_valid_nif",
            "has_delivery_address",
            "has_billing_address",
            "terms_accepted_at",
            "numero_cliente",
            "tipo_fidelidade_id",
        )

    def get_nif_masked(self, obj: Perfil) -> str | None:
        nif = (obj.nif or "").strip()
        if len(nif) == 9 and nif.isdigit():
            return f"{'*' * 6}{nif[-3:]}"
        return None

    def to_representation(self, instance: Perfil) -> dict[str, Any]:
        # English comment: never expose raw nif
        data = super().to_representation(instance)
        data.pop("nif", None)
        return data

    def validate_nif(self, value: str) -> str:
        if value is None:
            return value
        v = (value or "").strip()
        if v == "":
            return v
        if len(v) != 9 or not v.isdigit():
            raise serializers.ValidationError("O NIF tem de ter 9 dígitos.")
        if not validar_nif(v):
            raise serializers.ValidationError("NIF inválido.")
        return v

    def validate_telemovel(self, value: str) -> str:
        if value is None:
            return value
        v = (value or "").strip()
        if v == "":
            return v
        if len(v) != 9 or not v.isdigit():
            raise serializers.ValidationError("O telemóvel tem de ter 9 dígitos.")
        return v


class ProfileMePatchSerializer(serializers.Serializer):
    # English comment: composite payload { user: {...}, perfil: {...} }
    user = UserMePatchSerializer(required=False)
    perfil = PerfilSerializer(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if "user" not in attrs and "perfil" not in attrs:
            raise serializers.ValidationError("Nenhum campo para atualizar.")
        return attrs