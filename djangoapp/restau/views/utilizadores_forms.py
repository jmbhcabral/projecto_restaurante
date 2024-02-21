from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from fidelidade.forms import ComprasFidelidadeForm, OfertasFidelidadeForm
from fidelidade.models import ComprasFidelidade, OfertasFidelidade
from django.db import models


def compras_utilizador(request, utilizador_id):
    user = get_object_or_404(User, id=utilizador_id)

    initial_data = {
        'utilizador': user,
        'fidelidade': user.perfil.tipo_fidelidade.id,
    }

    if request.method == 'POST':
        form = ComprasFidelidadeForm(request.POST, initial=initial_data)

        if form.is_valid():
            compras = form.save(commit=False)
            compras.utilizador = user
            compras.fidelidade = user.perfil.tipo_fidelidade
            compras.save()
            return redirect(
                'restau:compras_utilizador',
                utilizador_id=utilizador_id
            )
    context = {
        'form': ComprasFidelidadeForm(initial=initial_data),
        'utilizador': user,
        'perfil': user.perfil,
    }

    return render(request, 'restau/pages/compras_utilizador.html', context)


def ofertas_utilizador(request, utilizador_id):
    user = get_object_or_404(User, id=utilizador_id)

    pontos_ganhos = ComprasFidelidade.objects.filter(
        utilizador=user).aggregate(
        total_pontos_ganhos=models.Sum('pontos_adicionados'))
    pontos_gastos = OfertasFidelidade.objects.filter(
        utilizador=user).aggregate(
        total_pontos_gastos=models.Sum('pontos_gastos'))

    pontos_ganhos_decimal = pontos_ganhos['total_pontos_ganhos'] or 0
    pontos_gastos_decimal = pontos_gastos['total_pontos_gastos'] or 0

    total_pontos = pontos_ganhos_decimal - pontos_gastos_decimal

    initial_data = {
        'utilizador': user,
        'fidelidade': user.perfil.tipo_fidelidade.id,
    }

    if request.method == 'POST':
        form = OfertasFidelidadeForm(request.POST, initial=initial_data)

        if form.is_valid():
            ofertas = form.save(commit=False)
            if ofertas.pontos_gastos is not None and \
                    total_pontos >= ofertas.pontos_gastos:
                ofertas.utilizador = user
                ofertas.fidelidade = user.perfil.tipo_fidelidade
                ofertas.save()
            else:
                messages.error(
                    request,
                    'Pontos insuficientes para realizar a oferta.'
                )
            return redirect(
                'restau:ofertas_utilizador',
                utilizador_id=utilizador_id
            )
        else:
            print('form.errors: ', form.errors)
    context = {
        'form': OfertasFidelidadeForm(initial=initial_data),
        'utilizador': user,
        'perfil': user.perfil,
    }

    return render(request, 'restau/pages/ofertas_utilizador.html', context)
