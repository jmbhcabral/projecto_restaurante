# djangoapp/perfil/api/views/profile_me.py
from __future__ import annotations

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from djangoapp.perfil.models import Perfil


class ProfileMeApiView(APIView):
    """
    GET /api/profile/me/
    PATCH /api/profile/me/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        perfil = (
            Perfil.objects
            .filter(usuario=user)
            .values(
                "id",
                "data_nascimento",
                "telemovel",
                "nif",
                "notificacoes_email",
                "notificacoes_telemovel",
                "terms_accepted_at",
            )
            .first()
        )

        if not perfil:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        # English comment: mask nif before returning
        nif_raw = perfil.get("nif") or ""
        perfil["nif_masked"] = (
            f"{'*' * 6}{nif_raw[-3:]}" if len(nif_raw) == 9 else None
        )
        perfil.pop("nif", None)

        # -------------------------
        # Add User fields
        # -------------------------
        perfil.update({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })

        return Response(perfil, status=status.HTTP_200_OK)

    def patch(self, request):
        with transaction.atomic():
            user = request.user

            perfil = Perfil.objects.filter(usuario=user).first()
            if not perfil:
                return Response({}, status=status.HTTP_404_NOT_FOUND)

            # -------------------------
            # Update User fields
            # -------------------------
            user_editable_fields = {"first_name", "last_name"}
            user_updated_fields = set()

            for field in user_editable_fields:
                if field in request.data:
                    setattr(user, field, request.data[field])
                    user_updated_fields.add(field)

            if user_updated_fields:
                user.full_clean()  # validates User model
                user.save(update_fields=list(user_updated_fields))

            # -------------------------
            # Update Perfil fields
            # -------------------------
            perfil_editable_fields = {
                "data_nascimento",
                "telemovel",
                "notificacoes_email",
                "notificacoes_telemovel",
            }
            perfil_updated_fields = set()

            for field in perfil_editable_fields:
                if field in request.data:
                    setattr(perfil, field, request.data[field])
                    perfil_updated_fields.add(field)

            if perfil_updated_fields:
                perfil.full_clean()  # runs model validations
                perfil.save(update_fields=list(perfil_updated_fields))

        return Response({"status": "updated"}, status=status.HTTP_200_OK)