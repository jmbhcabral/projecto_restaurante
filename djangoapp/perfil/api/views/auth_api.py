""" Este módulo contém as views para o login e registo do utilizador. """
# djangoapp/perfil/views/auth_api.py
from __future__ import annotations

from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from djangoapp.perfil.api.serializers.auth import (
    LoginSerializer,
    SignupResendSerializer,
    SignupStartSerializer,
    SignupVerifySerializer,
)


class SignupStartApiView(APIView):
    """
    POST /api/auth/signup/start/
    Body: { "email": "...", "password": "..." }
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_send"


    def post(self, request):
        serializer = SignupStartSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {
                "detail": "Código enviado.",
                "email": getattr(result, "email", None),
                "expires_at": getattr(result, "expires_at", None),
                "resend_count": getattr(result, "resend_count", None),
            },
            status=status.HTTP_200_OK,
        )


class SignupVerifyApiView(APIView):
    """
    POST /api/auth/signup/verify/
    Body: { "email": "...", "code": "123456" }
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_verify"

    def post(self, request):
        serializer = SignupVerifySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {
                "detail": "Conta verificada com sucesso.",
                "email": getattr(result, "email", None),
            },
            status=status.HTTP_200_OK,
        )


class SignupResendApiView(APIView):
    """
    POST /api/auth/signup/resend/
    Body: { "email": "..." }
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_send"

    def post(self, request):
        serializer = SignupResendSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {
                "detail": "Código reenviado.",
                "email": getattr(result, "email", None),
                "expires_at": getattr(result, "expires_at", None),
                "resend_count": getattr(result, "resend_count", None),
            },
            status=status.HTTP_200_OK,
        )


class LoginApiView(APIView):
    """
    POST /api/auth/login/
    Body: { "identifier": "...", "password": "..." }
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        login(request, user)

        return Response({"detail": "Login efetuado com sucesso."}, status=status.HTTP_200_OK)


class LogoutApiView(APIView):
    """
    POST /api/auth/logout/
    Session-based logout.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response({"detail": "Logout efetuado com sucesso."}, status=status.HTTP_200_OK)