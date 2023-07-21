from django.contrib import admin
from restau.models import (
    Category, SubCategory, Percentage, Produts
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'categoria'
    list_display_links = 'id', 'categoria'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'subcategoria'
    list_display_links = 'id', 'subcategoria'


@admin.register(Percentage)
class PercentagemAdmin(admin.ModelAdmin):
    list_display = 'id', 'valor'
    list_display_links = 'id', 'valor'


@admin.register(Produts)
class ProductsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nome', 'descricao_curta', 'descricao_longa', 'image',
        'preco', 'preco_promo', 'percentagem_desconto',
        'categoria', 'subcategoria', 'visibilidade')
    list_display_links = 'id', 'nome'
    search_fields = (
        'id', 'nome', 'descricao_curta', 'descricao_longa', 'image',
        'preco', 'preco_promo', 'percentagem_desconto',
        'categoria', 'subcategoria', 'visibilidade')
