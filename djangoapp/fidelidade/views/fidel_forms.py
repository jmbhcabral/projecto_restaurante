from django.shortcuts import render, redirect
from django.urls import reverse
from fidelidade.models import Fidelidade
from fidelidade.forms import FidelidadeForm


def criar_fidelidade(request):
    fidelidades = Fidelidade \
        .objects \
        .filter(nome__isnull=False)\
        .all()\
        .order_by('id')

    form_action = reverse('fidelidade:criar_fidelidade')

    if request.method == 'POST':
        form = FidelidadeForm(request.POST)

        context = {
            'fidelidades': fidelidades,
            'form': form,
            'form_action': form_action
        }

        if form.is_valid():
            form.save()
            return redirect('fidelidade:criar_fidelidade')

        return render(
            request,
            'fidelidade/pages/criar_fidelidade.html',
            context
        )
    context = {
        'fidelidades': fidelidades,
        'form': FidelidadeForm(),
        'form_action': form_action
    }

    return render(
        request,
        'fidelidade/pages/criar_fidelidade.html',
        context
    )
