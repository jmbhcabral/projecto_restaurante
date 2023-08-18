from django.urls import path
from restau.views import (                      # type: ignore
    index, admin_home, product, create_product, update, delete,
    encomendas, category, create_category, update_categories, delete_category
)

# namespace
app_name = 'restau'

urlpatterns = [
    path('', index, name='index'),
    path('restau/pages/encomendas/', encomendas, name='encomendas'),
    path('restau/pages/<int:product_id>/', product, name='product'),
    path('restau/pages/admin-home/', admin_home, name='admin-home'),
    path('restau/pages/create_product/',
         create_product, name='create_product'),
    path('restau/pages/<int:product_id>/update/', update, name='update'),
    path('restau/pages/<int:product_id>/delete/', delete, name='delete'),
    path('restau/pages/category/<int:category_id>/',
         category, name='category'),
    path('restau/pages/create_category/',
         create_category, name='create_category'),
    path('restau/pages/<int:category_id>/update_category/',
         update_categories, name='update_categories'),
    path('restau/pages/<int:category_id>/delete_category/',
         delete_category, name='delete_category'),
]
