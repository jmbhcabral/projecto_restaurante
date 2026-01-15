""" Este módulo contém as views para o JWT. """
# djangoapp/perfil/api/views/auth_jwt.py
from __future__ import annotations

from typing import cast

from django.contrib.auth.models import AbstractBaseUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from djangoapp.perfil.api.serializers.auth import LoginSerializer
from djangoapp.perfil.api.serializers.auth_jwt import LogoutJwtSerializer
from djangoapp.perfil.errors import CommonErrorCode, DomainError
from djangoapp.perfil.models import Perfil
from djangoapp.perfil.services.perfil_service import ensure_perfil_business_defaults


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

        # English comment: keep Perfil invariants consistent at login time
        perfil = Perfil.objects.filter(usuario=user).first()
        if perfil:
            ensure_perfil_business_defaults(perfil)

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


class LogoutJwtApiView(APIView):
    """
    POST /api/auth/logout/jwt/
    Body: { "refresh": "..." }
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_logout"  

    def post(self, request):
        serializer = LogoutJwtSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_str = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_str)
            token.blacklist()
        except TokenError:
            # do not reveal details (invalid/expired/etc.)
            raise DomainError(
                code=CommonErrorCode.BAD_REQUEST,
                message="Pedido inválido.",
                http_status=400,
            )

        return Response({"detail": "Logout efetuado com sucesso."}, status=status.HTTP_200_OK)