from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import Perfil
from ..serializers import UserRegistrationSerializer
from rest_framework.pagination import PageNumberPagination


class UsersAPIv1Pagination(PageNumberPagination):
    page_size = 20


class RegisterUserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    pagination_class = UsersAPIv1Pagination
    http_method_names = ['post', 'head', 'options', 'patch', 'get']

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
