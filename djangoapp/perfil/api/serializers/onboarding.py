from __future__ import annotations

from typing import Any

from rest_framework import serializers

from djangoapp.perfil.models import Perfil
from djangoapp.utils.model_validators import validar_nif


class OnboardingMinSerializer(serializers.Serializer):
    # Minimal onboarding fields (adapt to your UI)
    telemovel = serializers.CharField(required=False, allow_blank=True, max_length=9)
    nif = serializers.CharField(required=False, allow_blank=True, max_length=9)
    accept_terms = serializers.BooleanField(required=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs.get("accept_terms") is not True:
            raise serializers.ValidationError({"accept_terms": "Tens de aceitar os termos."})

        # Validate phone if provided
        telemovel = (attrs.get("telemovel") or "").strip()
        if telemovel:
            if len(telemovel) != 9 or not telemovel.isdigit():
                raise serializers.ValidationError({"telemovel": "O telemóvel tem de ter 9 dígitos."})

        # Validate nif if provided
        nif = (attrs.get("nif") or "").strip()
        if nif:
            if len(nif) != 9 or not nif.isdigit():
                raise serializers.ValidationError({"nif": "O NIF tem de ter 9 dígitos."})
            if not validar_nif(nif):
                raise serializers.ValidationError({"nif": "NIF inválido."})

        return attrs

    def save(self, **kwargs: Any) -> Perfil:
        # English comment: DRF's BaseSerializer.save signature is save(**kwargs)
        perfil = kwargs.get("perfil")
        if perfil is None or not isinstance(perfil, Perfil):
            raise TypeError("Missing required kwarg: perfil")

        data: dict[str, Any] = self.validated_data

        # Update fields
        if "telemovel" in data:
            perfil.telemovel = (data.get("telemovel") or "").strip()
        if "nif" in data:
            perfil.nif = (data.get("nif") or "").strip()

        # Set derived flags
        perfil.has_valid_nif = bool(perfil.nif and validar_nif(perfil.nif))

        # Mark onboarding minimal as completed
        perfil.onboarding_min_completed = True

        perfil.save()
        return perfil