from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)
from ..serializers import (
    MyTokenObtainPairSerializer, MyTokenRefreshSerializer
)

from rest_framework.response import Response
from ..models import Products, Category, SubCategory
from ..serializers import (
    ProdutoSerializer, CategoriaSerializer, SubCategoriaSerializer
)
from django.shortcuts import get_object_or_404
# from rest_framework import status
# from rest_framework.generics import (
#     ListCreateAPIView, RetrieveUpdateDestroyAPIView
# )
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from ..permissions import IsAcessoRestritoOrReadOnly


class ProdutosAPIv1Pagination(PageNumberPagination):
    page_size = 20


class ProdutosAPIv1ViewSet(ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProdutoSerializer
    pagination_class = ProdutosAPIv1Pagination
    permission_classes = [IsAcessoRestritoOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_object(self):
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        self.check_object_permissions(self.request, obj)

        return obj

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAcessoRestritoOrReadOnly()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        print('request: ', request.user)
        print('request: ', request.user.is_authenticated)

        return super().list(request, *args, **kwargs)


@api_view()
def categoria_api_detalhe(request, pk):
    categoria = get_object_or_404(
        Category.objects.all(),
        pk=pk,
    )
    serializer = CategoriaSerializer(
        instance=categoria,
        many=False,
        context={'request': request},
    )
    return Response(serializer.data)


@api_view()
def subcategoria_api_detalhe(request, pk):
    subcategoria = get_object_or_404(
        SubCategory.objects.all(),
        pk=pk,
    )
    serializer = SubCategoriaSerializer(
        instance=subcategoria,
        many=False,
        context={'request': request},
    )
    return Response(serializer.data)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer
