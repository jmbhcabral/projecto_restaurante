from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from fidelidade.forms import ComprasFidelidadeForm, OfertasFidelidadeForm
from fidelidade.models import ComprasFidelidade, OfertasFidelidade
from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime


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
        # 'fidelidade': user.perfil.tipo_fidelidade,
    }

    return render(request, 'restau/pages/compras_utilizador.html', context)


def ofertas_utilizador(request, utilizador_id):
    user = get_object_or_404(User, id=utilizador_id)

    agora = timezone.now()
    inicio_do_dia_atual = agora.replace(
        hour=0, minute=0, second=0, microsecond=0)
    inicio_para_uso_de_pontos = agora.replace(
        hour=11, minute=30, second=0, microsecond=0)

    if agora < inicio_para_uso_de_pontos:
        data_de_referencia = inicio_do_dia_atual - timezone.timedelta(days=1)
    else:
        data_de_referencia = inicio_do_dia_atual

    pontos_ganhos = ComprasFidelidade.objects.filter(
        utilizador=user, criado_em__lt=data_de_referencia).aggregate(
        total_pontos_ganhos=models.Sum('pontos_adicionados'))

    pontos_gastos = OfertasFidelidade.objects.filter(
        utilizador=user).aggregate(
        total_pontos_gastos=models.Sum('pontos_gastos'))

    pontos_ganhos_decimal = pontos_ganhos['total_pontos_ganhos'] or 0
    pontos_gastos_decimal = pontos_gastos['total_pontos_gastos'] or 0

    total_pontos_disponiveis = pontos_ganhos_decimal - pontos_gastos_decimal

    initial_data = {
        'utilizador': user,
        'fidelidade': user.perfil.tipo_fidelidade.id,
    }

    pontos_ganhos_totais = ComprasFidelidade.objects.filter(
        utilizador=user).aggregate(
        total_pontos_ganhos=models.Sum('pontos_adicionados'))

    pontos_gastos_totais = OfertasFidelidade.objects.filter(
        utilizador=user).aggregate(
        total_pontos_gastos=models.Sum('pontos_gastos'))

    total_pontos_ganhos_decimal = pontos_ganhos_totais['total_pontos_ganhos'] or 0
    total_pontos_gastos_decimal = pontos_gastos_totais['total_pontos_gastos'] or 0

    total_pontos = total_pontos_ganhos_decimal - total_pontos_gastos_decimal

    if request.method == 'POST':
        form = OfertasFidelidadeForm(request.POST, initial=initial_data)

        if form.is_valid():
            ofertas = form.save(commit=False)
            if ofertas.pontos_gastos is not None and \
                    total_pontos_disponiveis >= ofertas.pontos_gastos:
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
        'total_pontos': total_pontos,
        'total_pontos_disponiveis': total_pontos_disponiveis,
    }

    return render(request, 'restau/pages/ofertas_utilizador.html', context)
