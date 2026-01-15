# djangoapp/perfil/api/views/ping.py
from __future__ import annotations

from rest_framework.response import Response

from djangoapp.perfil.api.base import BasePrivateAPIView


class PingApiView(BasePrivateAPIView):
    """
    GET /api/ping/
    """
    def get(self, request):
        return Response({"message": "pong"})