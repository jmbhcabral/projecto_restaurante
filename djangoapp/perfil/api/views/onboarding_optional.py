# djangoapp/perfil/api/views/onboarding_optional.py
from __future__ import annotations

from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from djangoapp.fidelidade.services.profile_rewards import (
    try_award_profile_completed_bonus,
)
from djangoapp.perfil.models import Perfil
from djangoapp.perfil.services.onboarding_optional import (
    calc_optional_progress,
    optional_fields_state,
)


class OnboardingOptionalCompleteApiView(APIView):
    """
    POST /api/onboarding/optional/complete/
    Claim optional onboarding reward when profile is 100% complete.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            perfil = (
                Perfil.objects
                .select_for_update()
                .select_related("usuario")
                .get(usuario=request.user)
            )

            fields = optional_fields_state(perfil)
            missing = [k for k, ok in fields.items() if not ok]
            progress = calc_optional_progress(perfil)

            # English comment: if not complete, block reward claim
            if missing:
                return Response(
                    {
                        "detail": "Onboarding opcional incompleto.",
                        "optional_progress": progress,
                        "missing_fields": missing,
                        "onboarding_optional_completed": bool(perfil.onboarding_optional_completed),
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            # English comment: idempotent behavior (already completed/claimed)
            if perfil.onboarding_optional_completed:
                return Response(
                    {
                        "onboarding_optional_completed": True,
                        "optional_progress": 100,
                        "reward": {
                            "awarded": False,
                            "points": 1,
                            "code": "onboarding_optional_completed",
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            # Mark optional onboarding as completed
            perfil.onboarding_optional_completed = True
            perfil.save(update_fields=["onboarding_optional_completed"])

            # English comment: award points once after successful completion
            try_award_profile_completed_bonus(perfil.id, pontos=1)

        return Response(
            {
                "onboarding_optional_completed": True,
                "optional_progress": 100,
                "reward": {
                    "awarded": True,
                    "points": 1,
                    "code": "onboarding_optional_completed",
                },
            },
            status=status.HTTP_200_OK,
        )