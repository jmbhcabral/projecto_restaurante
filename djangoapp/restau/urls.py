from django.urls import path
from restau.views import (                      # type: ignore
    index, admin_home, produtos, produto, criar_produto, atualizar_produto,
    apagar_produto, encomendas, categoria, criar_categoria,
    atualizar_categoria, apagar_categoria, subcategoria, criar_subcategoria,
    atualizar_subcategoria, apagar_subcategoria, ordenar_produtos, ementas,
    criar_ementa, atualizar_ementa, apagar_ementa, povoar_ementa, ementa,
    configuracao, Subcategorias, ordenar_subcategorias, categorias,
    ordenar_categorias, adicionar_foto, galeria, povoar_galeria, imagem_logo
)

# namespace
app_name = 'restau'

urlpatterns = [
    path('', index, name='index'),
    path('restau/pages/encomendas/', encomendas, name='encomendas'),
    path('restau/pages/admin_home/', admin_home, name='admin_home'),
    # product
    path('restau/pages/produtos/', produtos, name='produtos'),
    path('restau/pages/<int:produto_id>/', produto, name='produto'),
    path('restau/pages/criar_produto/',
         criar_produto, name='criar_produto'),
    path('restau/pages/<int:produto_id>/atualizar_produto/',
         atualizar_produto, name='atualizar_produto'),
    path('restau/pages/<int:produto_id>/apagar_produto/',
         apagar_produto, name='apagar_produto'),
    path('restau/pages/ordenar_produtos/',
         ordenar_produtos, name='ordenar_produtos'),
    # category
    path('restau/pages/categorias/', categorias, name='categorias'),
    path('restau/pages/categoria/<int:categoria_id>/',
         categoria, name='categoria'),
    path('restau/pages/criar_categoria/',
         criar_categoria, name='criar_categoria'),
    path('restau/pages/<int:categoria_id>/atualizar_categoria/',
         atualizar_categoria, name='atualizar_categoria'),
    path('restau/pages/<int:categoria_id>/apagar_categoria/',
         apagar_categoria, name='apagar_categoria'),
    path('restau/pages/ordenar_categorias/',
         ordenar_categorias, name='ordenar_categorias'),
    # subcategoria
    path('restau/pages/subcategorias/', Subcategorias, name='subcategorias'),
    path('restau/pages/subcategoria/<int:subcategoria_id>/',
         subcategoria, name='subcategoria'),
    path('restau/pages/criar_subcategoria/',
         criar_subcategoria, name='criar_subcategoria'),
    path('restau/pages/<int:subcategoria_id>/atualizar_subcategoria/',
         atualizar_subcategoria, name='atualizar_subcategoria'),
    path('restau/pages/<int:subcategoria_id>/apagar_subcategoria/',
         apagar_subcategoria, name='apagar_subcategoria'),
    path('restau/pages/ordenar_subcategorias/',
         ordenar_subcategorias, name='ordenar_subcategorias'),
    # Ementas
    path('restau/pages/criar_ementa/', criar_ementa, name='criar_ementa'),
    path('restau/pages/<int:ementa_id>/atualizar_ementa/',
         atualizar_ementa, name='atualizar_ementa'),
    path('restau/pages/<int:ementa_id>/apagar_ementa/',
         apagar_ementa, name='apagar_ementa'),
    path('restau/pages/ementa/<int:ementa_id>/',
         ementa, name='ementa'),
    path('restau/pages/ementas/', ementas, name='ementas'),
    path('restau/pages/povoar_ementa/<int:ementa_id>/',
         povoar_ementa, name='povoar_ementa'),
    # Configuração
    path('restau/pages/configuracao/', configuracao, name='configuracao'),
    # Galeria
    path('restau/pages/galeria/', galeria, name='galeria'),
    path('restau/pages/adicionar_foto/',
         adicionar_foto, name='adicionar_foto'),
    path('restau/pages/povoar_galeria/',
         povoar_galeria, name='povoar_galeria'),
    # ImagemLogo
    path('restau/pages/logos/', imagem_logo, name='imagem_logo')
]
