from django.contrib import admin
from restau.models import (
    Category, SubCategory, Percentage, Products, FrontendSetup, Ementa,
    ProdutosEmenta, Fidelizacao,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'nome', 'ordem',
    list_display_links = 'id', 'nome'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'nome', 'categoria', 'ordem'
    list_display_links = 'id', 'nome'


@admin.register(Percentage)
class PercentagemAdmin(admin.ModelAdmin):
    list_display = 'id', 'valor'
    list_display_links = 'id', 'valor'


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nome', 'descricao_curta', 'descricao_longa', 'imagem',
        'preco_1', 'preco_2', 'preco_3', 'preco_4', 'preco_5', 'preco_6',
        'preco_promo', 'percentagem_desconto', 'categoria', 'subcategoria',
        'ordem', 'visibilidade'
    )

    list_display_links = 'id', 'nome'
    search_fields = (
        'id', 'nome', 'descricao_curta', 'descricao_longa', 'imagem',
        'preco_1', 'preco_2', 'preco_3', 'preco_4', 'preco_5', 'preco_6',
        'preco_promo', 'percentagem_desconto', 'categoria', 'subcategoria',
        'visibilidade'
    )


@admin.register(FrontendSetup)
class FrontendSetupAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'imagem_logo',
                    'imagem_topo', 'imagem_padrao',)
    list_display_links = ('id', 'nome', 'imagem_logo', 'imagem_topo',
                          'imagem_padrao',)


@admin.register(Ementa)
class EmentaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nome', 'descricao', 'nome_campo_preco_selecionado')
    list_display_links = (
        'id', 'nome', 'descricao', 'nome_campo_preco_selecionado')


@admin.register(ProdutosEmenta)
class ProdutosEmentaAdmin(admin.ModelAdmin):
    class ProdutosEmentaAdmin(admin.ModelAdmin):
        list_display = ('ementa', 'produtos_in_ementa',)

        # Vamos incluir um método customizado para representar produtos
        def produtos_in_ementa(self, obj):
            return ", ".join([str(p) for p in obj.produto.all()])

        produtos_in_ementa.short_description = 'Produtos na Ementa'


@admin.register(Fidelizacao)
class FidelizacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'unidade')
    list_display_links = ('id', 'nome', 'unidade')


# class ProdutosFidelizacaoAdmin(admin.ModelAdmin):
#     list_display = ('produto_fidelizacao',
#                     'get_pontos_recompensa', 'pontos_recompensa',
#                     'pontos_para_oferta'
#                     )

#     def get_pontos_recompensa(self, obj):
#         if obj.pontos_recompensa:
#             # Substitua 'preco' pelo nome real do campo de preço na classe
#             # Products
#             return obj.pontos_recompensa.preco
#         return 'N/A'

#     get_pontos_recompensa.pontos_recompensa = 'Pontos Recompensa'


# admin.site.register(ProdutosFidelizacao, ProdutosFidelizacaoAdmin)
