# djangoapp/perfil/api/views/me.py
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from djangoapp.perfil.models import Perfil


class MeApiView(APIView):
    """
    GET /api/auth/me/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_group_admin = user.groups.filter(name="acesso_restrito").exists()

        # minimal bootstrap payload (fast, stable, no personal data)
        perfil_data = (
            Perfil.objects
            .filter(usuario=user)
            .values(
                "id",
                "numero_cliente",
                "tipo_fidelidade_id",
                "onboarding_required_completed",
                "phone_verified",
                "has_valid_nif",
                "has_delivery_address",
                "has_billing_address",
            )
            .first()
        ) or {}

        return Response(
            {
                "id": user.id,
                "email": getattr(user, "email", None),
                "username": getattr(user, "username", None),
                "first_name": getattr(user, "first_name", None),
                "last_name": getattr(user, "last_name", None),
                "is_active": getattr(user, "is_active", None),
                "is_group_admin": is_group_admin,
                "perfil": {
                    "id": perfil_data.get("id"),
                    "numero_cliente": perfil_data.get("numero_cliente"),
                    "tipo_fidelidade": perfil_data.get("tipo_fidelidade_id"),
                    "onboarding_required_completed": bool(
                        perfil_data.get("onboarding_required_completed", False)
                    ),
                    "phone_verified": bool(perfil_data.get("phone_verified", False)),
                    "has_valid_nif": bool(perfil_data.get("has_valid_nif", False)),
                    "has_delivery_address": bool(perfil_data.get("has_delivery_address", False)),
                    "has_billing_address": bool(perfil_data.get("has_billing_address", False)),
                },
            }
        )