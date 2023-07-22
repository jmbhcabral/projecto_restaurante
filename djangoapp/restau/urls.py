from django.urls import path
from restau.views import index, adminsetup

# namespace
app_name = 'restau'

urlpatterns = [
    path('', index, name='index'),
    path('restau/pages/', adminsetup, name='adminsetup'),
]
