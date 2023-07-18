from django.urls import path
from restau.views import index

# namespace
app_name = 'restau'

urlpatterns = [
    path('', index, name='index'),
]
