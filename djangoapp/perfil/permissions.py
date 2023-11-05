from rest_framework import permissions


class IsAcessoRestrito(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.groups.filter(
            name='acesso_restrito').exists()


class IsOwner(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário
    de um objeto edite ou exclua.
    """

    def has_object_permission(self, request, view, obj):
        # print('has_object_permission: ', obj.id, request.user.id)
        # Só permite que o proprietário do objeto veja, edite ou exclua.
        return obj.id == request.user.id
