''' Arquivo de configuração de URL para o aplicativo senhas '''

from django.urls import path

from djangoapp.senhas.views import (
    adicionar_senha,
    listar_senhas,
    sistema_vez,
)

app_name = 'senhas'

urlpatterns = [
    path('sistema-de-vez/', sistema_vez, name='sistema_vez'),
    path('adicionar-numero/', adicionar_senha, name='adicionar_senha'),
    path('listar-numeros', listar_senhas, name='listar_senhas'),
]
