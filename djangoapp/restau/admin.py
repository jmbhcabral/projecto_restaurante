from django.contrib import admin
from django.utils.html import format_html
from restau.models import (
    Category, SubCategory, Percentage, Products, FrontendSetup, Ementa,
    ProdutosEmenta, Fotos, ActiveSetup
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
    list_display = ('id', 'nome', 'imagem_logo', 'imagem_topo', 'intro',
                    'intro_imagem', 'frase_inspiradora', 'imagem_frase_cima',
                    'frase_cima', 'frase_baixo',
                    'imagem_frase_baixo', 'imagem_padrao', 'ementa')
    list_display_links = ('id', 'nome', 'imagem_logo', 'imagem_topo',
                          'imagem_padrao', 'ementa')


@admin.register(ActiveSetup)
class ActiveSetupAdmin(admin.ModelAdmin):
    list_display = ('id', 'active_imagem_logo', 'active_imagem_topo',
                    'active_intro', 'active_intro_imagem',
                    'active_frase_inspiradora', 'active_imagem_frase_cima',
                    'active_frase_cima', 'active_frase_baixo',
                    'active_imagem_frase_baixo', 'active_imagem_padrao',
                    'active_ementa')
    list_display_links = ('id',)

    def has_add_permission(self, request):
        return not FrontendSetup.objects.exists()


@admin.register(Fotos)
class FotosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'imagem', 'image_thumb', 'is_visible',)
    list_display_links = ('id', 'nome', 'imagem',)
    list_editable = ('is_visible',)

    def image_thumb(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" width="50" height="50" />'.format(
                    obj.imagem.url)
            )
        return 'Sem Imagem'

    image_thumb.short_description = 'Miniatura'  # type: ignore

    # outra opção:
    # setattr(image_thumb, 'short_description', 'Miniatura')


@admin.register(Ementa)
class EmentaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nome', 'descricao', 'nome_campo_preco_selecionado')
    list_display_links = (
        'id', 'nome', 'descricao', 'nome_campo_preco_selecionado')


@admin.register(ProdutosEmenta)
class ProdutosEmentaAdmin(admin.ModelAdmin):
    list_display = ('ementa', 'produtos_in_ementa',)

    def produtos_in_ementa(self, obj):
        return ", ".join([str(p) for p in obj.produtos.all()])

    produtos_in_ementa.short_description = 'Produtos na Ementa'
