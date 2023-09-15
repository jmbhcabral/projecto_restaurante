from django.urls import path
from fidelidade.views import fidelidade, criar_fidelidade


app_name = 'fidelidade'

urlpatterns = [
    path('fidelidade/', fidelidade, name='fidelidade'),
    path(
        'fidelidade/criar_fidelidade',
        criar_fidelidade,
        name='criar_fidelidade'),
]
