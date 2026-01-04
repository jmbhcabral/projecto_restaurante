""" Este módulo contém os serializers para o JWT. """
# djangoapp/perfil/api/serializers/auth_jwt.py
from __future__ import annotations

from rest_framework import serializers


class LogoutJwtSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    

    def validate_refresh(self, value: str) -> str:
        token = (value or "").strip()
        if not token:
            raise serializers.ValidationError("Token inválido.")
        return token