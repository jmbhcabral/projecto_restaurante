from django.urls import path
from fidelidade.views import (
    fidelidades, criar_fidelidade, editar_fidelidade, apagar_fidelidade,
    fidelidade, pontos_produtos_fidelidade, util_ind_fidelidade,
)
from fidelidade.views.fidel_api import ProdutoFidelidadeAPI, TotalPontosAPIV1


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
        'fidelidade/fidelidade/<int:fidelidade_id>',
        fidelidade,
        name='fidelidade'),
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
    # API VIEWS
    path(
        'fidelidade/api/v1/produtos/<int:pk>/',

        ProdutoFidelidadeAPI.as_view(),
        name='produtos_fidelidade_api_v1'),
    path(
        'fidelidade/api/v1/pontos/<int:pk>/',
        TotalPontosAPIV1.as_view(),
        name='pontos_fidelidade_api_v1'),

]
