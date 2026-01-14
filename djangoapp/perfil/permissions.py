# djangoapp/perfil/permissions.py
from __future__ import annotations

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from djangoapp.perfil.models import Perfil


class IsAcessoRestrito(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.groups.filter(
            name="acesso_restrito"
        ).exists()


class IsOwner(permissions.BasePermission):
    """
    Custom permission to allow only the owner of an object to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id


class RequireOnboardingRequired(permissions.BasePermission):
    """
    Block authenticated users that have not completed required onboarding.
    Use together with IsAuthenticated on private endpoints.
    """

    message = "Perfil em falta ou onboarding por concluir."

    def has_permission(self, request: Request, view: APIView) -> bool:
        # let IsAuthenticated handle anonymous users
        if not request.user or not request.user.is_authenticated:
            return True

        # allow explicit opt-out for specific views
        if getattr(view, "allow_incomplete_onboarding", False):
            return True

        # cache profile on request to avoid duplicate database hits
        perfil: Perfil | None = getattr(request, "_perfil_cache", None)
        if perfil is None:
            try:
                perfil = Perfil.objects.only("id", "onboarding_required_completed").get(
                    usuario=request.user
                )
            except Perfil.DoesNotExist:
                return False
            setattr(request, "_perfil_cache", perfil)

        return bool(perfil.onboarding_required_completed)