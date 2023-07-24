from django.urls import path
from restau.views import index, admin_home

# namespace
app_name = 'restau'

urlpatterns = [
    path('', index, name='index'),
    path('restau/pages/admin-home', admin_home, name='admin-home'),
]
