""" Este módulo contém as views para o perfil do utilizador. """
# djangoapp/perfil/api/views/me.py
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class MeApiView(APIView):
    """
    GET /api/auth/me/
    Header: Authorization: Bearer <access>
    """
    permission_classes = [IsAuthenticated]
    # throttle_classes = [ScopedRateThrottle]
    # throttle_scope = "user"  

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "email": getattr(user, "email", None),
                "username": getattr(user, "username", None),
                "is_active": getattr(user, "is_active", None),
            }
        )