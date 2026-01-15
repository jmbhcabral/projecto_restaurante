# djangoapp/perfil/auth_backends.py
from __future__ import annotations

from django.contrib.auth import get_user_model

UserModel = get_user_model()


class IdentifierBackend:
    """
    Authenticate using an identifier that can be either:
    - email (preferred if there is an exact email match)
    - username (fallback)

    This is safe even if some usernames contain '@'.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not password:
            return None

        identifier = (username or kwargs.get("identifier") or "").strip()
        if not identifier:
            return None

        # 1) Try email exact match (case-insensitive)
        user = UserModel.objects.filter(email__iexact=identifier).first()

        # 2) Fallback to username exact match (case-insensitive)
        if user is None:
            user = UserModel.objects.filter(username__iexact=identifier).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def user_can_authenticate(self, user):
        return getattr(user, "is_active", True)

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None