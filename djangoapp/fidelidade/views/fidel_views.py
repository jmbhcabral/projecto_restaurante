from django.shortcuts import render, get_object_or_404, redirect
from fidelidade.models import Fidelidade, ComprasFidelidade, OfertasFidelidade
from fidelidade.forms import ComprasFidelidadeForm, OfertasFidelidadeForm
from django.contrib import messages
from django.db import models
from django.contrib.auth.models import User
from itertools import zip_longest


def fidelidades(request):
    def grouper(iterable, n, fillvalue=None):
        # "Coleta dados em grupos fixos"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    fidelidades = Fidelidade.objects.all()

    fidelidades_grouped = list(grouper(fidelidades, 5))

    context = {
        'fidelidades_grouped': fidelidades_grouped,
    }

    return render(
        request,
        'fidelidade/pages/fidelidades.html',
        context,
    )


def fidelidade(request, fidelidade_id):
    fidelidade = get_object_or_404(
        Fidelidade, pk=fidelidade_id
    )
    context = {
        'fidelidade': fidelidade
    }

    return render(
        request,
        'fidelidade/pages/fidelidade.html',
        context
    )


def util_ind_fidelidade(request, utilizador_pk):
    user = get_object_or_404(
        User, pk=utilizador_pk
    )

    pontos_ganhos = ComprasFidelidade.objects.filter(
        utilizador=user).aggregate(
        total_pontos_ganhos=models.Sum('pontos_adicionados'))
    pontos_gastos = OfertasFidelidade.objects.filter(
        utilizador=user).aggregate(
        total_pontos_gastos=models.Sum('pontos_gastos'))

    pontos_ganhos_decimal = pontos_ganhos['total_pontos_ganhos'] or 0
    pontos_gastos_decimal = pontos_gastos['total_pontos_gastos'] or 0

    total_pontos = pontos_ganhos_decimal - pontos_gastos_decimal

    if request.method == 'POST':
        form_type = request.POST.get('form_type', None)
        if form_type == 'compras':
            initial_data_compras = {
                'fidelidade': user.perfil.tipo_fidelidade.id,
                'utilizador': utilizador_pk,
            }
            compras_form = ComprasFidelidadeForm(
                request.POST, initial=initial_data_compras)

            if compras_form.is_valid():
                compras = compras_form.save(commit=False)
                compras.fidelidade_id = user.perfil.tipo_fidelidade.id
                compras.utilizador_id = utilizador_pk
                compras.save()
                return redirect(
                    'fidelidade:util_ind_fidelidade',
                    utilizador_pk=utilizador_pk
                )
            else:

                print('compras_form.errors: ', compras_form.errors)
        elif form_type == 'ofertas':
            initial_data_ofertas = {
                'fidelidade': user.perfil.tipo_fidelidade.id,
                'utilizador': utilizador_pk,
            }
            ofertas_form = OfertasFidelidadeForm(
                request.POST, initial=initial_data_ofertas)
            cleaned_data = ofertas_form.cleaned_data

            if ofertas_form.is_valid():
                ofertas = ofertas_form.save(commit=False)
                if ofertas.pontos_gastos is not None and \
                        total_pontos >= ofertas.pontos_gastos:
                    ofertas.fidelidade_id = user.perfil.tipo_fidelidade.id
                    ofertas.utilizador_id = utilizador_pk
                    ofertas.save()

                    return redirect(
                        'fidelidade:util_ind_fidelidade',
                        utilizador_pk=utilizador_pk
                    )
                else:
                    messages.error(
                        request,
                        'Preencha o campo pontos gastos com um valor válido')
            else:
                print('ofertas_form.errors: ', ofertas_form.errors)
    context = {
        'compras_form': ComprasFidelidadeForm(),
        'ofertas_form': OfertasFidelidadeForm(),
        'total_pontos': total_pontos,
        'utilizador': user,
        'perfil': user.perfil,
    }

    return render(
        request,
        'fidelidade/pages/util_ind_fidelidade.html',
        context)
