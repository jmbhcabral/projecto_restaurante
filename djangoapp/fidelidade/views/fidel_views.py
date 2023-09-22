from django.shortcuts import render, get_object_or_404
from fidelidade.models import Fidelidade
from perfil.models import Perfil


def fidelidade(request):
    utilizador = Perfil.objects.all()

    context = {
        'utilizador': utilizador
    }

    return render(
        request,
        'fidelidade/pages/fidelidade.html',
        context
    )


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
