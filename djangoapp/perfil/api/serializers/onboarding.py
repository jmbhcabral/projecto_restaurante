# djangoapp/perfil/api/serializers/onboarding.py
from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework import serializers

from djangoapp.fidelidade.models import RespostaFidelidade
from djangoapp.perfil.constants import QUESTION_CODE_STUDENT
from djangoapp.perfil.models import Perfil


class OnboardingRequiredSerializer(serializers.Serializer):
    estudante = serializers.PrimaryKeyRelatedField(
        queryset=RespostaFidelidade.objects.filter(
            resposta__pergunta__code=QUESTION_CODE_STUDENT
        ),
        required=True,
    )

    accept_terms = serializers.BooleanField(required=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs.get("accept_terms") is not True:
            raise serializers.ValidationError({"accept_terms": "Tens de aceitar os termos."})

        return attrs

    def save(self, **kwargs: Any) -> Perfil:
        perfil: Perfil | None = self.context.get("perfil")
        if perfil is None or not isinstance(perfil, Perfil):
            raise TypeError("Missing required context: perfil")

        resposta_fidelidade: RespostaFidelidade = self.validated_data["estudante"]

        # 1) Store the answer
        perfil.estudante = resposta_fidelidade

        # 2) Assign loyalty type derived from the answer
        perfil.tipo_fidelidade = resposta_fidelidade.tipo_fidelidade

        # 3) Mark onboarding as completed (blocking)
        perfil.onboarding_required_completed = True

        # 4) Store terms acceptance timestamp
        if perfil.terms_accepted_at is None:
            perfil.terms_accepted_at = timezone.now()

        perfil.save(
            update_fields=[
                "estudante",
                "tipo_fidelidade",
                "onboarding_required_completed",
                "terms_accepted_at",
            ]
        )
        return perfil


class StudentOptionSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="resposta.resposta")
    value = serializers.CharField(source="resposta.value")
    tipo_fidelidade = serializers.IntegerField(source="tipo_fidelidade_id")

    class Meta:
        model = RespostaFidelidade
        fields = [
            "id",
            "label",
            "value",
            "tipo_fidelidade",
        ]