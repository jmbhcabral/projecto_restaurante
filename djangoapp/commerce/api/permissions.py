# djangoapp/commerce/api/permissions.py
from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsCartOwner(BasePermission):
    """
    - For authenticated users: cart.user must match
    - For anonymous users: cart.session_key must match session
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if getattr(obj, "user_id", None) and request.user.is_authenticated:
            return obj.user_id == request.user.id

        # Anonymous cart ownership via session_key
        session_key = request.session.session_key or ""
        return bool(obj.session_key) and obj.session_key == session_key


class IsAccessRestricted(BasePermission):
    # Only users in acesso_restrito group can access admin endpoints
    message = "Sem permissões."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.groups.filter(name="acesso_restrito").exists()