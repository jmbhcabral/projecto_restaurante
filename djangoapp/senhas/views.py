''' Módulo de views do app senhas '''

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from djangoapp.senhas.models import FrasePub, Senhas


@login_required(login_url='/perfil')
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def sistema_vez(request):
    '''
    View para o sistema de senhas
    '''

    return render(
        request, 'senhas/pages/sistema-de-vez.html'
    )


@login_required(login_url='/perfil')
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def adicionar_senha(request):
    '''
    View para adicionar uma senha
    '''

    if request.method == 'POST':

        # Verifica se a requisição é AJAX e se o corpo contém dados em JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            body = json.loads(request.body)
            numero = body.get('numero')
        else:
            numero = request.POST.get('numero')
        print(f'Numero: {numero}')

        if numero:
            nova_senha = Senhas.objects.create(numero=numero)
            print(f'Nova senha: {nova_senha.numero}')

            messages.success(
                request, f'Senha {nova_senha.numero} adicionada com sucesso!'
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'numero': nova_senha.numero})

            return redirect(reverse('senhas:adicionar_senha'))

    return render(
        request, 'senhas/pages/adicionar-numero.html',

    )


@login_required(login_url='/perfil')
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def listar_senhas(request):
    '''
    View para listar as senhas
    '''

    # obter a data de hoje
    hoje = timezone.now().date()

    # obter as senhas criadas hoje
    senhas = Senhas.objects\
        .filter(created_at__date=hoje)\
        .order_by('-created_at')[:15]

    # obter a última senha criada
    ultima_senha = senhas.first().numero if senhas else None

    # mensagem de boas-vindas
    pub = FrasePub.objects.filter(  # pylint: disable=no-member
        escolhida=True).first()
    # contexto
    context = {
        'senhas': senhas,
        'ultima_senha': ultima_senha,
        'pub': pub
    }

    # verificar se a requisição é AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Se for AJAX, renderiza o template parcial de listagem de senhas
        senhas_html = render_to_string(
            'senhas/partials/_listar_senhas.html',
            {'senhas': senhas}
        )
        return JsonResponse(
            {
                'senhas_html': senhas_html,
                'ultima_senha': ultima_senha
            }
        )
    # Se não for AJAX, renderiza o template completo
    return render(
        request,
        'senhas/pages/listar-numeros.html',
        context
    )
