from rest_framework import permissions


class IsAcessoRestritoOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.groups.filter(
            name='acesso_restrito').exists()
