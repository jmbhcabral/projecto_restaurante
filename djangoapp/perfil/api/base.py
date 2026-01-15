# djangoapp/perfil/api/base.py
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from djangoapp.perfil.permissions import RequireOnboardingRequired


class BasePrivateAPIView(APIView):
    """
    - Default base class for private APIs.
    - Requires authenticated user + completed onboarding.
    """

    permission_classes = [IsAuthenticated, RequireOnboardingRequired]

    # set True on endpoints that must be accessible even if onboarding is incomplete
    allow_incomplete_onboarding: bool = False