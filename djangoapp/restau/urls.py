from django.urls import path
from restau.views import (                      # type: ignore
    index, admin_home, product, create_product, update, delete
)

# namespace
app_name = 'restau'

urlpatterns = [
    path('', index, name='index'),
    path('restau/pages/<int:product_id>/', product, name='product'),
    path('restau/pages/admin-home/', admin_home, name='admin-home'),
    path('restau/pages/create_product/', create_product, name='create_product'),
    path('restau/pages/<int:product_id>/update/', update, name='update'),
    path('restau/pages/<int:product_id>/delete/', delete, name='delete'),
]
