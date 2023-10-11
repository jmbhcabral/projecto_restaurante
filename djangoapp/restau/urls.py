from django.urls import path
from restau.views import (                      # type: ignore
    index, admin_home, produtos, product, create_product, update, delete,
    encomendas, category, create_category, update_categories, delete_category,
    subcategory, create_subcategory, update_subcategories, delete_subcategory,
    ordenar_produtos, ementas_create, ementas_update, ementas_delete, ementa,
    povoar_ementa, configuracao
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
    path('restau/pages/category/<int:category_id>/',
         category, name='category'),
    path('restau/pages/create_category/',
         create_category, name='create_category'),
    path('restau/pages/<int:category_id>/update_category/',
         update_categories, name='update_categories'),
    path('restau/pages/<int:category_id>/delete_category/',
         delete_category, name='delete_category'),
    # subcategory
    path('restau/pages/subcategory/<int:subcategory_id>/',
         subcategory, name='subcategory'),
    path('restau/pages/create_subcategory/',
         create_subcategory, name='create_subcategory'),
    path('restau/pages/<int:subcategory_id>/update_subcategory/',
         update_subcategories, name='update_subcategories'),
    path('restau/pages/<int:subcategory_id>/delete_subcategory/',
         delete_subcategory, name='delete_subcategory'),
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
