from django.shortcuts import render, get_object_or_404, redirect
from fidelidade.models import Fidelidade, ComprasFidelidade, OfertasFidelidade
from fidelidade.forms import ComprasFidelidadeForm, OfertasFidelidadeForm
from perfil.models import Perfil
from django.contrib import messages
from django.db import models
from django.contrib.auth.models import User
from django.http import QueryDict
from decimal import Decimal


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
            print('ofertas_form: ', ofertas_form.is_valid())
            cleaned_data = ofertas_form.cleaned_data
            print('ofertas cleaned_data: ', cleaned_data)

            if ofertas_form.is_valid():
                print('ofertas_form.is_valid')
                ofertas = ofertas_form.save(commit=False)
                print('total pontos: ', total_pontos)
                print('ofertas.pontos_gastos: ', ofertas.pontos_gastos)
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
                    print('ofertas_form.errors: ', ofertas_form.errors)
                    messages.error(
                        request,
                        'Preencha o campo pontos gastos com um valor válido')
                    # return redirect(
                    #     'fidelidade:util_ind_fidelidade',
                    #     utilizador_pk=utilizador_pk
                    # )
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
