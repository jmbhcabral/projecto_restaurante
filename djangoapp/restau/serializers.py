from rest_framework import serializers
from .models import Category, SubCategory, Products
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = [
            'id', 'nome', 'descricao_curta', 'descricao_longa', 'categoria',
            'categoria_nome', 'categoria_links', 'subcategoria',
            'subcategoria_nome', 'subcategoria_links', 'preco_1', 'preco_2',
            'preco_3', 'preco_4', 'preco_5', 'preco_6', 'imagem', 'ordem',
            'visibilidade'
        ]
    # categoria = serializers.PrimaryKeyRelatedField(
    #     queryset=Category.objects.all(),
    # )
    categoria_nome = serializers.StringRelatedField(
        source='categoria.nome',
        read_only=True,
    )
    categoria_links = serializers.HyperlinkedRelatedField(
        source='categoria',
        # queryset=Category.objects.all(),
        view_name='restau:produto_categoria_api_v1',
        read_only=True,
    )

    # subcategoria = serializers.PrimaryKeyRelatedField(
    #     queryset=SubCategory.objects.all(),
    # )
    subcategoria_nome = serializers.StringRelatedField(
        source='subcategoria.nome',
        read_only=True,
    )
    subcategoria_links = serializers.HyperlinkedRelatedField(
        source='subcategoria',
        # queryset=SubCategory.objects.all(),
        view_name='restau:produto_subcategoria_api_v1',
        read_only=True,
    )


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'nome', 'ordem']

    # id = serializers.IntegerField()
    # nome = serializers.CharField(max_length=200)
    # ordem = serializers.IntegerField()

# ModelSerializer so precisamos declarar os campos que alteramos


class SubCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = [
            'id', 'nome', 'categoria', 'categoria_nome', 'categoria_links',
            'ordem'
        ]
    # id = serializers.IntegerField()
    # nome = serializers.CharField(max_length=200)
    # categoria = serializers.PrimaryKeyRelatedField(
    #     queryset=Category.objects.all(),
    # )
    categoria_nome = serializers.StringRelatedField(
        source='categoria.nome',
    )
    categoria_links = serializers.HyperlinkedRelatedField(
        source='categoria',
        queryset=Category.objects.all(),
        view_name='restau:produto_categoria_api_v1'
    )
    # ordem = serializers.IntegerField()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Assegurando que o atributo 'id' existe
        user_id = getattr(self.user, 'id', None)
        if user_id is not None:
            data['user_id'] = user_id
        else:
            raise serializers.ValidationError("ID de usuário não encontrado.")

        return data
