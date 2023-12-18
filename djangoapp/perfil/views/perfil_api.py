from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from ..serializers import (
    UserRegistrationSerializer, )
from rest_framework.pagination import PageNumberPagination
from ..permissions import IsAcessoRestrito, IsOwner
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from perfil.models import Perfil


class UsersAPIv1Pagination(PageNumberPagination):
    page_size = 20


class RegisterUserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    pagination_class = UsersAPIv1Pagination
    permission_classes = [IsAcessoRestrito, IsOwner]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        # Restringir a lista de usuários para apenas aqueles que estão
        # ao grupo de acesso restrito.
        if self.action == 'list':
            if self.request.user.groups.filter(name='acesso_restrito').exists():
                return User.objects.all().order_by('id')
            else:
                raise PermissionDenied(
                    "Você não tem permissão para listar os usuários."
                )
        return super().get_queryset()

    def get_object(self):
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        self.check_object_permissions(self.request, obj)

        return obj

    def get_permissions(self):
        # Se a ação for 'create', ou seja, registro de novo usuário,
        # permitir que qualquer pessoa acesse a API.
        if self.action == 'create':
            return [AllowAny()]

        # Se a ação for 'list', ou seja, listagem de usuários,
        # permitir que apenas usuários autenticados e que pertençam
        # ao grupo de acesso restrito acessem a API.
        elif self.action == 'list':
            return [IsAcessoRestrito()]

        # Somente o dono do usuário pode alterar ou excluir o registro.
        elif self.action in ['retrieve', 'partial_update', 'destroy']:
            return [IsOwner()]

        else:
            # Caso contrário, retornar as permissões padrão.
            permission_classes = self.permission_classes

        # Retorna instancias das classes de permissão
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )

        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user_instance = get_object_or_404(User, pk=pk)
        perfil_instance = Perfil.objects.filter(
            usuario=user_instance).first()

        print('user_instance', user_instance)
        print('request.data', request.data)
        print('request.user', request.user)
        print('request.user.id', request.user.id)

        # Passando a instância para o serializador
        serializer = UserRegistrationSerializer(
            user_instance,
            data=request.data,
            partial=True,
            context={
                'perfil_instance': perfil_instance,
                'request': request,
            }
        )

        print('serializer', serializer)

        if serializer.is_valid():
            serializer.save()
            print('serializer.data', serializer.data)
            return Response(serializer.data)
        else:
            print('serializer.errors', serializer.errors)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
