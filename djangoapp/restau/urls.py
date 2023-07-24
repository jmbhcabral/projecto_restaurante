from django.urls import path
from restau.views import index, admin_home, create_product

# namespace
app_name = 'restau'

urlpatterns = [
    path('', index, name='index'),
    path('restau/pages/admin-home', admin_home, name='admin-home'),
    path('restau/pages/create_product', create_product, name='create_product'),
]
