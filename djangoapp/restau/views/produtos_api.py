from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Products, Category, SubCategory
from ..serializers import ProdutoSerializer, CategoriaSerializer
from django.shortcuts import get_object_or_404


@api_view()
def lista_produtos_api(request):
    produtos = Products.objects.all()
    serializer = ProdutoSerializer(
        instance=produtos,
        many=True,
        context={'request': request},
    )
    return Response(serializer.data)


@api_view()
def detalhe_produtos_api(request, pk):
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
    # produto = Products.objects.filter(pk=pk).first()

    # if produto:
    #     serializer = ProdutoSerializer(instance=produto, many=False)
    #     return Response(serializer.data)
    # else:
    #     return Response(
    #         {'detail': 'Não existe.'},
    #         status=404,
    #     )


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
