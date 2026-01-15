# djangoapp/perfil/api/views/profile_me.py
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from djangoapp.perfil.api.serializers.profile import (
    PerfilSerializer,
    ProfileMePatchSerializer,
    UserMeSerializer,
)
from djangoapp.perfil.models import Perfil
from djangoapp.perfil.services.profile_me_service import update_me_profile


class ProfileMeApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        perfil = Perfil.objects.filter(usuario=user).first()
        if not perfil:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "user": UserMeSerializer(user).data,
                "perfil": PerfilSerializer(perfil, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        s = ProfileMePatchSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)

        result = update_me_profile(user=request.user, payload=s.validated_data)

        return Response(
            {
                "status": "updated",
                "user_updated": result.user_updated,
                "perfil_updated": result.perfil_updated,
            },
            status=status.HTTP_200_OK,
        )