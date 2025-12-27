from collections import defaultdict
from typing import Any, ClassVar

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from djangoapp.restau.models import (
    Category,
    Ementa,
    Products,
    ProdutosEmenta,
    SubCategory,
    VersaoApp,
)


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome: ClassVar[serializers.StringRelatedField]
    categoria_links: ClassVar[serializers.HyperlinkedRelatedField]
    subcategoria_nome: ClassVar[serializers.StringRelatedField]
    subcategoria_links: ClassVar[serializers.HyperlinkedRelatedField]

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
    categoria_nome: ClassVar[serializers.StringRelatedField]
    categoria_links: ClassVar[serializers.HyperlinkedRelatedField]

    class Meta:
        model = SubCategory
        fields = [
            'id', 'nome', 'categoria', 'categoria_nome', 'categoria_links',
            'ordem'
        ]

    categoria_nome = serializers.StringRelatedField(
        source='categoria.nome',
    )
    categoria_links = serializers.HyperlinkedRelatedField(
        source='categoria',
        queryset=Category.objects.all(),
        view_name='restau:produto_categoria_api_v1'
    )


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: dict[str, Any]) -> Any:
        try:
            data = super().validate(attrs)
            
            # Adiciona o ID do usuário aos dados retornados
            data['user_id'] = self.user.id
            
            
            return data
            
        except Exception as e:
            error_message = str(e)
            if "No active account found" in error_message:
                raise serializers.ValidationError({
                    "error": "Utilizador e/ou password inválidos"
                })
            elif "This field may not be blank" in error_message:
                raise serializers.ValidationError({
                    "error": "Os campos de Utilizador e Password são obrigatórios."
                })
            else:
                raise serializers.ValidationError({
                    "error": "Erro ao fazer login. Por favor, tente novamente."
                })


class MyTokenRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs: dict[str, Any]) -> Any:
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


# class ProdutosPorSubcategoriaSerializer(serializers.ModelSerializer):
#     produtos = serializers.SerializerMethodField()

#     class Meta:
#         model = SubCategory
#         fields = [
#             'id', 'nome', 'produtos'
#         ]

#     def get_produtos(self, subcategoria):
#         produtos = Products.objects.filter(
#             subcategoria=subcategoria,
#             ementas__id=self.context['ementa_id']
#         ).order_by('ordem')
#         return ProdutoSerializer(
#             produtos,
#             many=True,
#             context=self.context
#         ).data


# class CategoriaComSubcategoriaSerializer(serializers.ModelSerializer):
#     subcategorias = serializers.SerializerMethodField()

#     class Meta:
#         model = Category
#         fields = [
#             'id', 'nome', 'subcategorias'
#         ]

#     def get_subcategorias(self, categoria):
#         subcategorias = SubCategory.objects.filter(
#             categoria=categoria
#         ).order_by('ordem')
#         return ProdutosPorSubcategoriaSerializer(
#             subcategorias,
#             many=True,
#             context=self.context
#         ).data


class ProdutoEmentaSerializer(serializers.ModelSerializer):
    preco_dinamico = serializers.SerializerMethodField()
    descricao_final = serializers.SerializerMethodField()
    
    class Meta:
        model = Products
        fields = [
            'id', 'nome', 'descricao_final', 'descricao_longa', 
            'imagem', 'ordem', 'visibilidade', 'preco_dinamico'
        ]
    
    def get_preco_dinamico(self, produto):
        ementa = self.context.get('ementa')
        if ementa:
            campo_preco = ementa.nome_campo_preco_selecionado
            return getattr(produto, campo_preco, 0.00)
        return 0.00
    
    def get_descricao_final(self, produto):
        produto_ementa = self.context.get('produto_ementa', {}).get(produto.id)
        if produto_ementa and produto_ementa.descricao:
            return produto_ementa.descricao
        return produto.descricao_curta


class SubCategoriaEmentaSerializer(serializers.ModelSerializer):
    produtos = serializers.SerializerMethodField()
    
    class Meta:
        model = SubCategory
        fields = ['id', 'nome', 'ordem', 'produtos']
        
    def get_produtos(self, subcategoria):
        ementa = self.context.get('ementa')
        produtos = Products.objects.filter(
            subcategoria=subcategoria,
            visibilidade=True
        ).order_by('ordem')
        
        return ProdutoEmentaSerializer(
            produtos, 
            many=True,
            context={'ementa': ementa}
        ).data


class CategoriaEmentaSerializer(serializers.ModelSerializer):
    subcategorias = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'nome', 'ordem', 'subcategorias']
        
    def get_subcategorias(self, categoria):
        subcategorias = SubCategory.objects.filter(
            categoria=categoria
        ).order_by('ordem')
        
        return SubCategoriaEmentaSerializer(
            subcategorias,
            many=True,
            context=self.context
        ).data


class ProdutosEmentaSerializer(serializers.ModelSerializer):
    categorias = serializers.SerializerMethodField()
    
    class Meta:
        model = Ementa
        fields = [
            'id', 'nome', 'descricao', 
            'nome_campo_preco_selecionado', 'categorias'
        ]
        
    def get_categorias(self, ementa):
        # Buscar produtos da ementa com suas descrições personalizadas
        produtos_ementa = ProdutosEmenta.objects.filter(
            ementa=ementa,
            produto__visibilidade=True
        ).select_related(
            'produto', 
            'produto__categoria', 
            'produto__subcategoria'
        ).order_by('produto__ordem')

        # Criar dicionário para mapear produtos e suas descrições personalizadas
        produtos_ementa_dict = {pe.produto.id: pe for pe in produtos_ementa}
        
        # Dicionário para armazenar categorias e subcategorias ordenadas
        categorias_dict = defaultdict(lambda: {'subcategorias': defaultdict(list)})
        
        for pe in produtos_ementa:
            if pe.produto:
                produto = pe.produto
                cat = produto.categoria
                subcat = produto.subcategoria
                
                if cat:  # Se o produto tem categoria
                    categorias_dict[cat]['subcategorias'][subcat].append(produto)
        
        # Ordenar e formatar os dados para serialização
        categorias_formatadas = []
        for cat, cat_data in sorted(categorias_dict.items(), key=lambda x: x[0].ordem if x[0] else 0):
            if cat:  # Verificar se a categoria não é None
                subcategorias_formatadas = []
                # Ordenar subcategorias
                sorted_subcats = sorted(
                    cat_data['subcategorias'].items(), 
                    key=lambda x: x[0].ordem if x[0] else 0
                )
                
                for subcat, produtos in sorted_subcats:
                    # Ordenar produtos dentro da subcategoria
                    produtos_ordenados = sorted(produtos, key=lambda p: p.ordem)
                    
                    subcategoria_data = {
                        'id': subcat.id if subcat else None,
                        'nome': subcat.nome if subcat else "Sem Subcategoria",
                        'ordem': subcat.ordem if subcat else 0,
                        'produtos': ProdutoEmentaSerializer(
                            produtos_ordenados,
                            many=True,
                            context={
                                'ementa': ementa,
                                'produto_ementa': produtos_ementa_dict
                            }
                        ).data
                    }
                    subcategorias_formatadas.append(subcategoria_data)
                
                categoria_data = {
                    'id': cat.id,
                    'nome': cat.nome,
                    'ordem': cat.ordem,
                    'subcategorias': subcategorias_formatadas
                }
                categorias_formatadas.append(categoria_data)
        
        return categorias_formatadas


class VersaoAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersaoApp
        fields = [
            'numero_versao', 'url_download', 'notas_versao', 'data_lancamento'
        ]
