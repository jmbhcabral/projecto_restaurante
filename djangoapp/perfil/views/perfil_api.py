from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from ..models import Perfil
from ..serializers import (
    UserRegistrationSerializer, PerfilSerializer, UserPerfilSerializer)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny


class UsersAPIv1Pagination(PageNumberPagination):
    page_size = 20


class RegisterUserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    pagination_class = UsersAPIv1Pagination
    http_method_names = ['post']

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


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPerfilSerializer
    permission_classes = [AllowAny]
    pagination_class = UsersAPIv1Pagination
    http_method_names = ['get']


class UserPerfilView(generics.RetrieveUpdateAPIView):
    serializer_class = PerfilSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return Perfil.objects.filter(usuario=self.request.user)

    def get_object(self):
        perfil, _ = Perfil.objects.get_or_create(
            usuario=self.request.user)

        return perfil
