from django.urls import path
from restau.views import (                      # type: ignore
    index, admin_home, produtos, product, create_product, update, delete,
    encomendas, categoria, criar_categoria, atualizar_categoria,
    apagar_categoria, subcategoria, criar_subcategoria, atualizar_subcategoria,
    apagar_subcategoria, ordenar_produtos, ementas_create, ementas_update,
    ementas_delete, ementa, povoar_ementa, configuracao, Subcategorias,
    ordenar_subcategorias, categorias, ordenar_categorias
)

# namespace
app_name = 'restau'

urlpatterns = [
    path('', index, name='index'),
    path('restau/pages/encomendas/', encomendas, name='encomendas'),
    path('restau/pages/admin_home/', admin_home, name='admin_home'),
    # product
    path('restau/pages/produtos/', produtos, name='produtos'),
    path('restau/pages/ordenar_produtos/',
         ordenar_produtos, name='ordenar_produtos'),
    path('restau/pages/<int:product_id>/', product, name='product'),
    path('restau/pages/create_product/',
         create_product, name='create_product'),
    path('restau/pages/<int:product_id>/update/', update, name='update'),
    path('restau/pages/<int:product_id>/delete/', delete, name='delete'),
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
    path('restau/pages/ementas/', ementas_create, name='ementas_create'),
    path('restau/pages/<int:ementa_id>/ementas_update/',
         ementas_update, name='ementas_update'),
    path('restau/pages/<int:ementa_id>/ementas_delete/',
         ementas_delete, name='ementas_delete'),
    path('restau/pages/ementa/<int:ementa_id>/',
         ementa, name='ementa'),
    path('restau/pages/povoar_ementa/<int:ementa_id>/',
         povoar_ementa, name='povoar_ementa'),
    # Configuração
    path('restau/pages/configuracao/', configuracao, name='configuracao'),

]
