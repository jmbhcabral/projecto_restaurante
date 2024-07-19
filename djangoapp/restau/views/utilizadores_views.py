from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from perfil.models import Perfil
from fidelidade.models import ComprasFidelidade, OfertasFidelidade
from django.db import models
from operator import attrgetter
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def admin_utilizadores(request, *args, **kwargs):
    query = request.GET.get('query', None)

    if query is not None:
        resultado_completo = f'CEW-{query}'
        try:
            perfil = Perfil.objects.get(numero_cliente=resultado_completo)
            if perfil.tipo_fidelidade is None:
                messages.error(
                    request,
                    f'Cliente {resultado_completo} não tem fidelidade atribuida')
                return redirect(
                    'restau:admin_utilizadores')
            else:
                usuario = User.objects.get(pk=perfil.usuario.id)
                return redirect(
                    'restau:compras_utilizador',
                    utilizador_pk=usuario.pk)
        except Perfil.DoesNotExist:
            messages.error(
                request,
                f'Cliente {resultado_completo} não encontrado')

    return render(request, 'restau/pages/admin_utilizadores.html')


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def admin_utilizador(request, utilizador_pk):
    user = get_object_or_404(User, pk=utilizador_pk)

    ultima_compra = ComprasFidelidade.objects.filter(
        utilizador=user).order_by('-criado_em').first()

    ultima_oferta = OfertasFidelidade.objects.filter(
        utilizador=user).order_by('-criado_em').first()

    if ultima_compra:
        dias_sem_comprar = (datetime.now().date() -
                            ultima_compra.criado_em.date()).days
    else:
        dias_sem_comprar = 'Nunca comprou.'

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
        'ultima_compra': ultima_compra,
        'ultima_oferta': ultima_oferta,
        'dias_sem_comprar': dias_sem_comprar,
    }
    return render(
        request,
        'restau/pages/admin_utilizador.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def movimentos(request, utilizador_id):
    user = get_object_or_404(User, pk=utilizador_id)

    compras = ComprasFidelidade.objects.filter(
        utilizador=user).order_by('-criado_em')

    ofertas = OfertasFidelidade.objects.filter(
        utilizador=user).order_by('-criado_em')

    registros_combinados = list(compras) + list(ofertas)

    registros_ordenados = sorted(
        registros_combinados,
        key=attrgetter('criado_em'),
        reverse=True
    )

    context = {
        'registros_ordenados': registros_ordenados,
        'utilizador': user,
        'compras': compras,
        'ofertas': ofertas,
    }
    return render(
        request,
        'restau/pages/movimentos_compras_ofertas.html',
        context
    )
