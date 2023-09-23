from django.shortcuts import render, get_object_or_404, redirect
from fidelidade.models import Fidelidade
from perfil.models import Perfil
from django.contrib import messages


def fidelidade(request):
    query = request.GET.get('query', '')
    resultado_completo = f'CEW-{query}'

    if Perfil.objects.filter(numero_cliente=resultado_completo).exists():
        utilizador = Perfil.objects.get(numero_cliente=resultado_completo)
        print(utilizador)
        print(utilizador.pk)
        context = {
            'utilizador': utilizador
        }

        return render(
            request,
            'fidelidade/pages/fidelidade.html',
            context
        )

    else:
        messages.error(
            request,
            'Número de cliente não encontrado')
        return render(request, 'fidelidade/pages/fidelidade.html')


def fidelidade_individual(request, fidelidade_id):
    fidelidade_individual = get_object_or_404(
        Fidelidade, pk=fidelidade_id
    )
    context = {
        'fidelidade': fidelidade_individual
    }

    return render(
        request,
        'fidelidade/pages/fidelidade_ind.html',
        context
    )


def util_ind_fidelidade(request, utilizador_pk):
    utilizador = get_object_or_404(
        Perfil, pk=utilizador_pk
    )

    if utilizador.numero_cliente:
        util_ind_fidelidade = get_object_or_404(
            Perfil, utilizador_id=utilizador
        )

        context = {
            'util_ind_fidelidade': util_ind_fidelidade
        }

        return render(
            request,
            'fidelidade/pages/util_ind_fidelidade.html',
            context
        )
    else:
        messages.error(
            request,
            'Número de cliente não encontrado')
        return render(
            request,
            'fidelidade/pages/fidelidade.html')
