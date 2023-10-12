from django.urls import path
from fidelidade.views import (
    fidelidades, criar_fidelidade, editar_fidelidade, apagar_fidelidade,
    fidelidade_individual, pontos_produtos_fidelidade, util_ind_fidelidade)


app_name = 'fidelidade'

urlpatterns = [
    path('fidelidade/fidelidades', fidelidades, name='fidelidades'),
    path('fidelidade/util_ind_fidelidade/<int:utilizador_pk>',
         util_ind_fidelidade, name='util_ind_fidelidade'),
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
    path(
        'fidelidade/pontos_produtos/<int:fidelidade_id>',
        pontos_produtos_fidelidade,
        name='pontos_produtos_fidelidade'),
]
