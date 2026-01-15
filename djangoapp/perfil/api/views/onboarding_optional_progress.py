# djangoapp/perfil/api/views/onboarding_optional_progress.py
from __future__ import annotations

from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from djangoapp.perfil.api.serializers.onboarding_optional_progress import (
    OnboardingOptionalProgressSerializer,
)
from djangoapp.perfil.models import Perfil
from djangoapp.perfil.services.onboarding_optional import (
    calc_optional_progress,
    optional_fields_state,
    should_show_optional_banner,
)


class OnboardingOptionalProgressApiView(APIView):
    """
    GET  /api/onboarding/optional/        -> get progress for banner/UI
    PATCH /api/onboarding/optional/       -> save partial progress
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        perfil = (
            Perfil.objects
            .select_related("usuario")
            .only(
                "id",
                "usuario__first_name",
                "usuario__last_name",
                "telemovel",
                "data_nascimento",
                "onboarding_required_completed",
                "onboarding_optional_completed",
            )
            .get(usuario=request.user)
        )

        fields = optional_fields_state(perfil)
        missing = [k for k, ok in fields.items() if not ok]
        progress = calc_optional_progress(perfil)

        return Response(
            {
                "optional_progress": progress,
                "onboarding_optional_completed": bool(perfil.onboarding_optional_completed),
                "optional_fields": fields,
                "missing_fields": missing,
                "show_optional_banner": should_show_optional_banner(perfil),
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        with transaction.atomic():
            perfil = (
                Perfil.objects
                .select_for_update()
                .select_related("usuario")
                .get(usuario=request.user)
            )

            serializer = OnboardingOptionalProgressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(perfil=perfil)

            # English comment: refresh fields needed to compute progress accurately
            perfil.refresh_from_db(
                fields=[
                    "telemovel",
                    "data_nascimento",
                    "onboarding_required_completed",
                    "onboarding_optional_completed",
                ]
            )
            # user fields might have changed (first/last name)
            perfil.usuario.refresh_from_db(fields=["first_name", "last_name"])

            fields = optional_fields_state(perfil)
            missing = [k for k, ok in fields.items() if not ok]
            progress = calc_optional_progress(perfil)

        return Response(
            {
                "optional_progress": progress,
                "onboarding_optional_completed": bool(perfil.onboarding_optional_completed),
                "optional_fields": fields,
                "missing_fields": missing,
                "show_optional_banner": should_show_optional_banner(perfil),
            },
            status=status.HTTP_200_OK,
        )