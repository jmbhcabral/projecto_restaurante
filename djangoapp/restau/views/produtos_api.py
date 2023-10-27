from rest_framework.decorators import api_view
from rest_framework.views import APIView

from rest_framework.response import Response
from ..models import Products, Category, SubCategory
from ..serializers import (
    ProdutoSerializer, CategoriaSerializer, SubCategoriaSerializer
)
from django.shortcuts import get_object_or_404
from rest_framework import status


class ProdutosAPIv1View(APIView):
    def get(self, request):
        produtos = Products.objects.all()
        serializer = ProdutoSerializer(
            instance=produtos,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = ProdutoSerializer(
            data=request.data
        )
        if serializer.is_valid():
            return Response(
                serializer.validated_data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ProdutoAPIv1Detalhe(APIView):
    def get_produto(self, pk):
        produto = get_object_or_404(
            Products.objects.all(),
            pk=pk,
        )
        return produto

    def get(self, request, pk):
        produto = self.get_produto(pk)
        serializer = ProdutoSerializer(
            instance=produto,
            many=False,
            context={'request': request},
        )
        return Response(serializer.data)

    def patch(self, request, pk):
        produto = self.get_produto(pk)
        serializer = ProdutoSerializer(
            instance=produto,
            data=request.data,
            many=False,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data
        )

    def delete(self, request, pk):
        produto = self.get_produto(pk)
        produto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
