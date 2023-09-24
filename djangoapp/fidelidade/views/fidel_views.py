from django.shortcuts import render, get_object_or_404, redirect
from fidelidade.models import Fidelidade, ComprasFidelidade, OfertasFidelidade
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

    # total_pontos = (pontos_ganhos['total_pontos_ganhos'] -
    #                 pontos_gastos['total_pontos_gastos'])

    context = {
        'total_pontos': total_pontos,
        'utilizador': user,
        'perfil': user.perfil,
    }

    return render(
        request,
        'fidelidade/pages/util_ind_fidelidade.html',
        context)
