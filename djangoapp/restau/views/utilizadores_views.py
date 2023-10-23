from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from perfil.models import Perfil
from fidelidade.models import ComprasFidelidade, OfertasFidelidade
from django.db import models


def admin_utilizadores(request):
    query = request.GET.get('query', None)

    if query is not None:
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
                    'restau:admin_utilizadores')
            else:
                usuario = User.objects.get(pk=perfil.usuario.id)
                print('Tipo fidelidade is not None')
                print('fidelidade id: ', perfil.tipo_fidelidade.id)
                print('Utilizador id: ', perfil.usuario.id)
                print('Utilizador master id: ', usuario.id)
                return redirect(
                    'restau:admin_utilizador',
                    utilizador_pk=usuario.pk)
        except Perfil.DoesNotExist:
            messages.error(
                request,
                f'Cliente {resultado_completo} não encontrado')

    return render(request, 'restau/pages/admin_utilizadores.html')


def admin_utilizador(request, utilizador_pk):
    user = get_object_or_404(User, pk=utilizador_pk)

    pontos_ganhos = ComprasFidelidade.objects.filter(
        utilizador=user).aggregate(
        total_pontos_ganhos=models.Sum('pontos_adicionados'))
    pontos_gastos = OfertasFidelidade.objects.filter(
        utilizador=user).aggregate(
        total_pontos_gastos=models.Sum('pontos_gastos'))

    pontos_ganhos_decimal = pontos_ganhos['total_pontos_ganhos'] or 0
    pontos_gastos_decimal = pontos_gastos['total_pontos_gastos'] or 0

    total_pontos = pontos_ganhos_decimal - pontos_gastos_decimal

    context = {
        'utilizador': user,
        'perfil': user.perfil,
        'total_pontos': total_pontos,
    }
    return render(
        request,
        'restau/pages/admin_utilizador.html',
        context
    )

    # return render(request, 'restau/pages/admin_utilizador.html')
