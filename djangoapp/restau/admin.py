from django.contrib import admin
from restau.models import (
    Category, SubCategory, Percentage, Products, FrontendSetup, Fidelizacao,
    ProdutosFidelizacao
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
        'preco', 'preco_promo', 'percentagem_desconto',
        'categoria', 'subcategoria', 'ordem', 'visibilidade')
    list_display_links = 'id', 'nome'
    search_fields = (
        'id', 'nome', 'descricao_curta', 'descricao_longa', 'imagem',
        'preco', 'preco_promo', 'percentagem_desconto',
        'categoria', 'subcategoria', 'visibilidade')


@admin.register(FrontendSetup)
class FrontendSetupAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'imagem_logo',
                    'imagem_topo', 'imagem_padrao',)
    list_display_links = ('id', 'nome', 'imagem_logo', 'imagem_topo',
                          'imagem_padrao',)


@admin.register(Fidelizacao)
class FidelizacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'unidade')
    list_display_links = ('id', 'nome', 'unidade')


class ProdutosFidelizacaoAdmin(admin.ModelAdmin):
    list_display = ('produto_fidelizacao',
                    'get_pontos_recompensa', 'pontos_para_oferta')

    def get_pontos_recompensa(self, obj):
        if obj.pontos_recompensa:
            # Substitua 'preco' pelo nome real do campo de preço na classe
            # Products
            return obj.pontos_recompensa.preco
        return 'N/A'

    get_pontos_recompensa.short_description = 'Pontos Recompensa'


admin.site.register(ProdutosFidelizacao, ProdutosFidelizacaoAdmin)
