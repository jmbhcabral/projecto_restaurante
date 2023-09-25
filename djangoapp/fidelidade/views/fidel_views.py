from django.shortcuts import render, get_object_or_404, redirect
from fidelidade.models import Fidelidade, ComprasFidelidade, OfertasFidelidade
from fidelidade.forms import ComprasFidelidadeForm, OfertasFidelidadeForm
from perfil.models import Perfil
from django.contrib import messages
from django.db import models
from django.contrib.auth.models import User


def fidelidade(request):
    query = request.GET.get('query', None)

    if query is not None:
        resultado_completo = f'CEW-{query}'

        try:
            perfil = Perfil.objects.get(numero_cliente=resultado_completo)
            return redirect(
                'fidelidade:util_ind_fidelidade',
                utilizador_pk=perfil.pk)
        except Perfil.DoesNotExist:
            messages.error(
                request,
                f'Cliente {resultado_completo} não encontrado')
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


def util_ind_fidelidade(request, utilizador_pk):
    user = get_object_or_404(
        User, perfil__pk=utilizador_pk
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
        print(request.POST)
        if 'adicionar_pontos' in request.POST:
            compras_form = ComprasFidelidadeForm(
                request.POST,  utilizador_pk=utilizador_pk)
            if compras_form.is_valid():
                print(compras_form.is_valid)
                print(compras_form.cleaned_data['pontos_adicionados'])
                compras_form.save()
                messages.success(
                    request,
                    f'Pontos adicionados com sucesso a {user.username}')
                return redirect(
                    'fidelidade:util_ind_fidelidade',
                    utilizador_pk=utilizador_pk)
            else:
                messages.error(
                    request,
                    'Erro ao adicionar pontos')
                return redirect(
                    'fidelidade:util_ind_fidelidade',
                    utilizador_pk=utilizador_pk)
        elif 'ofertar_pontos' in request.POST:
            ofertas_form = OfertasFidelidadeForm(
                request.POST, utilizador_pk=utilizador_pk)
            if ofertas_form.is_valid():
                ofertas_form.save()
                messages.success(
                    request,
                    f'Pontos ofertados com sucesso a {user.username}')
                return redirect(
                    'fidelidade:util_ind_fidelidade',
                    utilizador_pk=utilizador_pk)
            else:
                messages.error(
                    request,
                    'Erro ao ofertar pontos')
                return redirect(
                    'fidelidade:util_ind_fidelidade',
                    utilizador_pk=utilizador_pk)

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
