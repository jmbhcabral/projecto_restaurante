from django.urls import path
from fidelidade.views import fidelidade


app_name = 'fidelidade'

urlpatterns = [
    path('fidelidade/', fidelidade, name='fidelidade'),
]
