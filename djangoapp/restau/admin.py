from django.contrib import admin
from django.utils.html import format_html
from restau.models import (
    Category, SubCategory, Percentage, Products, Ementa,
    ProdutosEmenta, Fotos, ActiveSetup, ImagemLogo, ImagemTopo, Intro,
    IntroImagem, FraseInspiradora, ImagemFraseCima, FraseCima, FraseBaixo,
    ImagemFraseBaixo, ImagemPadrao, ContactosSite, GoogleMaps, Horario,
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


@admin.register(ImagemLogo)
class ImagemLogoAdmin(admin.ModelAdmin):
    list_display = ('id', 'imagem', 'is_visible')
    list_display_links = ('id', 'imagem', 'is_visible')


@admin.register(ImagemTopo)
class ImagemTopoAdmin(admin.ModelAdmin):
    list_display = ('id', 'imagem', 'is_visible')
    list_display_links = ('id', 'imagem', 'is_visible')


@admin.register(Intro)
class IntroAdmin(admin.ModelAdmin):
    list_display = ('id', 'texto', 'is_visible')
    list_display_links = ('id', 'texto', 'is_visible')


@admin.register(IntroImagem)
class IntroImagemAdmin(admin.ModelAdmin):
    list_display = ('id', 'imagem', 'is_visible')
    list_display_links = ('id', 'imagem', 'is_visible')


@admin.register(FraseInspiradora)
class FraseInspiradoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'texto', 'is_visible')
    list_display_links = ('id', 'texto', 'is_visible')


@admin.register(ImagemFraseCima)
class ImagemFraseCimaAdmin(admin.ModelAdmin):
    list_display = ('id', 'imagem', 'is_visible')
    list_display_links = ('id', 'imagem', 'is_visible')


@admin.register(FraseCima)
class FraseCimaAdmin(admin.ModelAdmin):
    list_display = ('id', 'texto', 'is_visible')
    list_display_links = ('id', 'texto', 'is_visible')


@admin.register(FraseBaixo)
class FraseBaixoAdmin(admin.ModelAdmin):
    list_display = ('id', 'texto', 'is_visible')
    list_display_links = ('id', 'texto', 'is_visible')


@admin.register(ImagemFraseBaixo)
class ImagemFraseBaixoAdmin(admin.ModelAdmin):
    list_display = ('id', 'imagem', 'is_visible')
    list_display_links = ('id', 'imagem', 'is_visible')


@admin.register(ImagemPadrao)
class ImagemPadraoAdmin(admin.ModelAdmin):
    list_display = ('id', 'imagem', 'is_visible')
    list_display_links = ('id', 'imagem', 'is_visible')


@admin.register(ContactosSite)
class ContactosSiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'morada', 'telefone', 'email', 'facebook',
                    'instagram')
    list_display_links = ('id', 'morada', 'telefone', 'email', 'facebook',
                          'instagram')

    def has_add_permission(self, request):
        return not ContactosSite.objects.exists()


@admin.register(GoogleMaps)
class GoogleMapsAdmin(admin.ModelAdmin):
    list_display = ('id', 'iframe')
    list_display_links = ('id', 'iframe')

    def has_add_permission(self, request):
        return not GoogleMaps.objects.exists()


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'dia_semana')
    list_display_links = ('id', 'dia_semana')


@admin.register(ActiveSetup)
class ActiveSetupAdmin(admin.ModelAdmin):
    list_display = ('id', 'active_imagem_logo', 'active_imagem_topo',
                    'active_intro', 'active_intro_imagem',
                    'active_frase_inspiradora', 'active_imagem_frase_cima',
                    'active_frase_cima', 'active_frase_baixo',
                    'active_imagem_frase_baixo', 'active_imagem_padrao',
                    'active_ementa', 'active_contactos_site',
                    'active_google_maps',)
    list_display_links = ('id',)

    def has_add_permission(self, request):
        return not ActiveSetup.objects.exists()


@admin.register(Fotos)
class FotosAdmin(admin.ModelAdmin):
    list_display = ('id', 'imagem',
                    'image_thumb', 'is_visible', 'ordem',)
    list_display_links = ('id', 'imagem',)
    list_editable = ('is_visible', 'ordem',)

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
        return ", ".join([str(p) for p in obj.produto.all()])

    produtos_in_ementa.short_description = 'Produtos na Ementa'
