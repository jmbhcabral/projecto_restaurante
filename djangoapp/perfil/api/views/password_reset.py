# djangoapp/perfil/api/views/password_reset.py
from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from djangoapp.perfil.api.serializers.password_reset import (
    PasswordResetResendSerializer,
    PasswordResetStartSerializer,
    PasswordResetVerifySerializer,
)


class PasswordResetStartApiView(APIView):
    """
    POST /api/auth/password/reset/start/
    Body: { "email": "..." }
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_send"

    def post(self, request):
        serializer = PasswordResetStartSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        # keep response neutral to avoid email enumeration.
        return Response(
            {
                "detail": "Se o email existir, enviámos um código.",
                "email": getattr(result, "email", None),
                "expires_at": None,      # force neutral
                "resend_count": None,    # force neutral
            },
            status=status.HTTP_200_OK,
        )

class PasswordResetResendApiView(APIView):
    """
    POST /api/auth/password/reset/resend/
    Body: { "email": "..." }
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_send"

    def post(self, request):
        serializer = PasswordResetResendSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {
                "detail": "Se o email existir, reenviámos o código.",
                "email": getattr(result, "email", None),
                "expires_at": None,
                "resend_count": None,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetVerifyApiView(APIView):
    """
    POST /api/auth/password/reset/verify/
    Body: { "email": "...", "code": "123456", "new_password": "..." }
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_verify"

    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {
                "detail": "Password alterada com sucesso.",
                "email": getattr(result, "email", None),
            },
            status=status.HTTP_200_OK,
        )