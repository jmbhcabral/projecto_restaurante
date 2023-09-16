from django.urls import path
from fidelidade.views import (
    fidelidade, criar_fidelidade, editar_fidelidade, apagar_fidelidade,
    fidelidade_individual)


app_name = 'fidelidade'

urlpatterns = [
    path('fidelidade/', fidelidade, name='fidelidade'),
    path(
        'fidelidade/criar_fidelidade',
        criar_fidelidade,
        name='criar_fidelidade'),
    path(
        'fidelidade/fidelidade_ind/<int:fidelidade_id>',
        fidelidade_individual,
        name='fidelidade_individual'),
    path(
        'fidelidade/editar_fidelidade/<int:fidelidade_id>',
        editar_fidelidade,
        name='editar_fidelidade'),
    path(
        'fidelidade/apagar_fidelidade/<int:fidelidade_id>',
        apagar_fidelidade,
        name='apagar_fidelidade'),
]
