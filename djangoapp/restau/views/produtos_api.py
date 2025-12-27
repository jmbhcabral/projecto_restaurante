from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from ..models import Category, Ementa, Products, SubCategory
from ..permissions import IsAcessoRestritoOrReadOnly
from ..serializers import (
    CategoriaSerializer,
    MyTokenObtainPairSerializer,
    MyTokenRefreshSerializer,
    ProdutosEmentaSerializer,
    ProdutoSerializer,
    SubCategoriaSerializer,
)


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
        return super().list(request, *args, **kwargs)
    

# @api_view()
# def produtos_api_detalhe(request, pk):
#     produto = get_object_or_404(
#         Products.objects.all(),
#         pk=pk,
#     )
#     serializer = ProdutoSerializer(
#         instance=produto,
#         many=False,
#         context={'request': request},
#     )
#     return Response(serializer.data)

class ProdutosAPIv1DetailView(APIView):
    def get(self, request, pk):
        produto = get_object_or_404(
            Products.objects.all(),
            pk=pk,
        )
        serializer = ProdutoSerializer(
            instance=produto,
            many=False,
            context={'request': request},
        )
        return Response(serializer.data)


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


class UserEmentaAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return Response(
                {'detail': 'Não autorizado'},
                status=401,
            )
        try:
            ementa = user.perfil.tipo_fidelidade.ementa
            produtos_ementa = Ementa.objects.filter(
                id=ementa.id,
            )

            serializer = ProdutosEmentaSerializer(
                produtos_ementa,
                many=True,
                context={'request': request},
            )

            return Response(serializer.data)
        except Ementa.DoesNotExist:
            return Response(
                {'detail': 'Não existe ementa para este utilizador'},
                status=404,
            )
