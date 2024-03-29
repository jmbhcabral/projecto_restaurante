from rest_framework import serializers
from .models import Category, SubCategory, Products
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer, TokenRefreshSerializer
)
from .models import Ementa, VersaoApp


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

    subcategoria_nome = serializers.StringRelatedField(
        source='subcategoria.nome',
        read_only=True,
    )
    subcategoria_links = serializers.HyperlinkedRelatedField(
        source='subcategoria',
        view_name='restau:produto_subcategoria_api_v1',
        read_only=True,
    )


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'nome', 'ordem']

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


class MyTokenRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        # Chame o método validate da classe pai para
        # realizar a validação padrão
        data = super().validate(attrs)

        # O refresh token estará disponível em data.get('refresh')
        refresh_token = data.get('refresh')

        if refresh_token:
            # Faça o que você precisa com o refresh token, como imprimir
            print(f'Refresh token: {refresh_token}')
        else:
            # Caso a chave 'refresh' não esteja presente nos dados
            print('Refresh token not found in data')

        # Exemplo de log
        self.message('Token refresh successful!')

        return data

    def message(self, message):
        print(message)


class ProdutosPorSubcategoriaSerializer(serializers.ModelSerializer):
    produtos = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = [
            'id', 'nome', 'produtos'
        ]

    def get_produtos(self, subcategoria):
        produtos = Products.objects.filter(
            subcategoria=subcategoria,
            ementas__id=self.context['ementa_id']
        ).order_by('ordem')
        return ProdutoSerializer(
            produtos,
            many=True,
            context=self.context
        ).data


class CategoriaComSubcategoriaSerializer(serializers.ModelSerializer):
    subcategorias = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'nome', 'subcategorias'
        ]

    def get_subcategorias(self, categoria):
        subcategorias = SubCategory.objects.filter(
            categoria=categoria
        ).order_by('ordem')
        return ProdutosPorSubcategoriaSerializer(
            subcategorias,
            many=True,
            context=self.context
        ).data


class ProdutosEmentaSerializer(serializers.ModelSerializer):
    categorias = serializers.SerializerMethodField()

    class Meta:
        model = Ementa
        fields = [
            'nome', 'descricao', 'nome_campo_preco_selecionado', 'categorias',
        ]

    def get_categorias(self, obj):
        subcategorias_ids = obj.produtos.all().values_list(
            'subcategoria', flat=True
        )
        categorias = Category.objects.filter(
            subcategory__id__in=subcategorias_ids
        ).distinct().order_by('ordem')
        return CategoriaComSubcategoriaSerializer(
            categorias,
            many=True,
            context={'ementa_id': obj.id, 'request': self.context['request']})\
            .data


class VersaoAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersaoApp
        fields = [
            'numero_versao', 'url_download', 'notas_versao', 'data_lancamento'
        ]
