from rest_framework.decorators import api_view
# from rest_framework.views import APIView

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
    page_size = 5


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

# class ProdutosAPIv1View(ListCreateAPIView):
#     queryset = Products.objects.all()
#     serializer_class = ProdutoSerializer
#     pagination_class = ProdutosAPIv1Pagination
    # def get(self, request):
    #     produtos = Products.objects.all()
    #     serializer = ProdutoSerializer(
    #         instance=produtos,
    #         many=True,
    #         context={'request': request},
    #     )
    #     return Response(serializer.data)

    # def post(self, request):
    #     serializer = ProdutoSerializer(
    #         data=request.data
    #     )
    #     if serializer.is_valid():
    #         return Response(
    #             serializer.validated_data,
    #             status=status.HTTP_201_CREATED,
    #         )
    #     return Response(
    #         serializer.errors,
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )


# class ProdutoAPIv1Detalhe(RetrieveUpdateDestroyAPIView):
#     queryset = Products.objects.all()
#     serializer_class = ProdutoSerializer
#     pagination_class = ProdutosAPIv1Pagination

    # def get_produto(self, pk):
    #     produto = get_object_or_404(
    #         Products.objects.all(),
    #         pk=pk,
    #     )
    #     return produto

    # def get(self, request, pk):
    #     produto = self.get_produto(pk)
    #     serializer = ProdutoSerializer(
    #         instance=produto,
    #         many=False,
    #         context={'request': request},
    #     )
    #     return Response(serializer.data)

    # def patch(self, request, pk):
    #     produto = self.get_produto(pk)
    #     serializer = ProdutoSerializer(
    #         instance=produto,
    #         data=request.data,
    #         many=False,
    #         context={'request': request},
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(
    #         serializer.data
    #     )

    # def delete(self, request, pk):
    #     produto = self.get_produto(pk)
    #     produto.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


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
