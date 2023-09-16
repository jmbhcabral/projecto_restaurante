from django.shortcuts import render, get_object_or_404
from fidelidade.models import Fidelidade


def fidelidade(request):

    return render(
        request,
        'fidelidade/pages/fidelidade.html',
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
