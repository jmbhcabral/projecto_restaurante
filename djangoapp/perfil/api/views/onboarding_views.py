# djangoapp/perfil/api/views/onboarding_views.py
from __future__ import annotations

from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from djangoapp.fidelidade.models import RespostaFidelidade
from djangoapp.perfil.api.serializers.onboarding import (
    OnboardingRequiredSerializer,
    StudentOptionSerializer,
)
from djangoapp.perfil.models import Perfil


class OnboardingCompleteApiView(APIView):
    """
    Completes required onboarding (student + terms).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            perfil = (
                Perfil.objects
                .select_for_update()
                .get(usuario=request.user)
            )

            if perfil.onboarding_required_completed:
                return Response(
                    {"onboarding_required_completed": True, "tipo_fidelidade": perfil.tipo_fidelidade_id},
                    status=status.HTTP_200_OK,
                )

            serializer = OnboardingRequiredSerializer(
                data=request.data,
                context={"perfil": perfil},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            perfil.refresh_from_db(fields=["tipo_fidelidade_id", "onboarding_required_completed"])

        return Response(
            {
                "onboarding_required_completed": True,
                "tipo_fidelidade": perfil.tipo_fidelidade_id,
            },
            status=status.HTTP_200_OK,
        )


QUESTION_CODE_STUDENT = "student_status"

class OnboardingStudentOptionsApiView(APIView):
    """
    Returns available options for the 'student status' onboarding question.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        qs = (
            RespostaFidelidade.objects
            .select_related("resposta", "tipo_fidelidade", "resposta__pergunta")
            .filter(resposta__pergunta__code=QUESTION_CODE_STUDENT)
            .order_by("id")
        )

        serializer = StudentOptionSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)