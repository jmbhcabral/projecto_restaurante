from rest_framework import serializers
from .models import Category, SubCategory


class ProdutoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nome = serializers.CharField(max_length=100)
    descricao_curta = serializers.CharField(max_length=200)
    descricao_longa = serializers.CharField(max_length=500)
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
    )
    categoria_nome = serializers.StringRelatedField(
        source='categoria.nome',
    )
    categoria_links = serializers.HyperlinkedRelatedField(
        source='categoria',
        queryset=Category.objects.all(),
        view_name='restau:produto_categoria_api_v1'
    )

    subcategoria = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all(),
    )
    subcategoria_nome = serializers.StringRelatedField(
        source='subcategoria.nome',
    )
    imagem = serializers.CharField(max_length=200)
    ordem = serializers.IntegerField()
    visibilidade = serializers.BooleanField()


class CategoriaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nome = serializers.CharField(max_length=200)
    ordem = serializers.IntegerField()
