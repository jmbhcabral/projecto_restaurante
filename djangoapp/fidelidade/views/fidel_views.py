from django.shortcuts import render, get_object_or_404, redirect
from fidelidade.models import Fidelidade, ComprasFidelidade, OfertasFidelidade
from fidelidade.forms import ComprasFidelidadeForm, OfertasFidelidadeForm
from perfil.models import Perfil
from django.contrib import messages
from django.db import models
from django.contrib.auth.models import User
from django.http import QueryDict


def fidelidade(request):
    query = request.GET.get('query', None)
    print('Query: ', query)

    if query is not None:
        print('Query not None')
        resultado_completo = f'CEW-{query}'

        try:
            perfil = Perfil.objects.get(numero_cliente=resultado_completo)
            print('Perfil:', perfil)
            if perfil.tipo_fidelidade is None:
                print('Tipo fidelidade is None')
                messages.error(
                    request,
                    f'Cliente {resultado_completo} não tem fidelidade atribuida')
                return redirect(
                    'fidelidade:fidelidade')
            else:
                usuario = User.objects.get(pk=perfil.usuario.id)
                print('Tipo fidelidade is not None')
                print('fidelidade id: ', perfil.tipo_fidelidade.id)
                print('Utilizador id: ', perfil.usuario.id)
                print('Utilizador master id: ', usuario.id)
                return redirect(
                    'fidelidade:util_ind_fidelidade',
                    utilizador_pk=usuario.pk)
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
        print('REQUEST.POST', request.POST)
        print('UTILIZADOR_ID: ', utilizador_pk)
        print('FIDELIDADE_ID: ', user.perfil.tipo_fidelidade.id)

        initial_data = {
            'fidelidade': user.perfil.tipo_fidelidade.id,
            'utilizador': utilizador_pk,
        }
        print('INITIAL_DATA: ', initial_data)

        compras_form = ComprasFidelidadeForm(
            request.POST, initial=initial_data)
        print('VALIDO: ', compras_form.is_valid())
        cleaned_data = compras_form.cleaned_data
        print('CLEANED_DATA: ', cleaned_data)
        if compras_form.is_valid():
            print('compras_form.is_valid()')
            compras = compras_form.save(commit=False)
            compras.fidelidade_id = user.perfil.tipo_fidelidade.id
            print('FIDELIDADE_ID: ', compras.fidelidade_id)
            compras.utilizador_id = utilizador_pk
            print('UTILIZADOR_ID: ', compras.utilizador_id)
            cleaned_data = compras_form.cleaned_data
            print('Cleaned data after: ', compras_form.cleaned_data)
            compras.save()
            return redirect(
                'fidelidade:util_ind_fidelidade',
                utilizador_pk=utilizador_pk
            )
        else:
            print('compras_form.errors: ', compras_form.errors)
    context = {
        'compras_form': ComprasFidelidadeForm(),
        # 'ofertas_form': OfertasFidelidadeForm(),
        'total_pontos': total_pontos,
        'utilizador': user,
        'perfil': user.perfil,
    }

    return render(
        request,
        'fidelidade/pages/util_ind_fidelidade.html',
        context)
