""" Este módulo contém as views para o JWT. """
# djangoapp/perfil/api/views/auth_jwt.py
from __future__ import annotations

from typing import cast

from django.contrib.auth.models import AbstractBaseUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from djangoapp.perfil.api.serializers.auth import LoginSerializer


class LoginJwtApiView(APIView):
    """
    POST /api/auth/login/jwt/
    Body: { "identifier": "...", "password": "..." }
    Returns: { "access": "...", "refresh": "..." }
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user: AbstractBaseUser = serializer.validated_data["user"]

        refresh = cast(RefreshToken, RefreshToken.for_user(user))
        access = str(refresh.access_token)

        return Response(
            {
                "detail": "Login efetuado com sucesso.",
                "access": access,
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )