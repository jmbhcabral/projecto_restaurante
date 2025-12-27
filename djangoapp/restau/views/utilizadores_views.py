from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from djangoapp.fidelidade.ledger import get_movimentos_pontos
from djangoapp.fidelidade.models import ComprasFidelidade, OfertasFidelidade
from djangoapp.perfil.models import Perfil
from djangoapp.utils.model_validators import (
    calcular_total_pontos,
    calcular_total_pontos_disponiveis,
)


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

    hoje = timezone.localdate()
    ultima_visita = ComprasFidelidade.objects.filter(
        utilizador=user,
        criado_em__date__lt=hoje
    ).order_by('-criado_em').first()
    ultima_compra = ComprasFidelidade.objects.filter(
        utilizador=user).order_by('-criado_em').first()

    ultima_oferta = OfertasFidelidade.objects.filter(
        utilizador=user).order_by('-criado_em').first()

    if ultima_compra:
        dias_sem_comprar = (datetime.now().date() -
                            ultima_compra.criado_em.date()).days
    else:
        dias_sem_comprar = 'Nunca comprou.'

    if ultima_oferta:
        dias_sem_oferta = (datetime.now().date() -
                           ultima_oferta.criado_em.date()).days
    else:
        dias_sem_oferta = 'Nunca recebeu uma oferta.'

    total_pontos = calcular_total_pontos(user)
    print(f'total_pontos: {total_pontos}')

    total_pontos_disponiveis = calcular_total_pontos_disponiveis(user)
    print(f'total_pontos_disponiveis: {total_pontos_disponiveis}')

    context = {
        'utilizador': user,
        'perfil': user.perfil,
        'total_pontos': total_pontos,
        'total_pontos_disponiveis': total_pontos_disponiveis,
        'ultima_visita': ultima_visita,
        'ultima_compra': ultima_compra,
        'ultima_oferta': ultima_oferta,
        'dias_sem_comprar': dias_sem_comprar,
        'dias_sem_oferta': dias_sem_oferta,
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

    # compras = ComprasFidelidade.objects.filter(
    #     utilizador=user).order_by('-criado_em')

    # ofertas = OfertasFidelidade.objects.filter(
    #     utilizador=user).order_by('-criado_em')

    # registros_combinados = list(compras) + list(ofertas)

    # registros_ordenados = sorted(
    #     registros_combinados,
    #     key=attrgetter('criado_em'),
    #     reverse=True
    # )

    movimentos_user = get_movimentos_pontos(user)

    context = {
        'movimentos': movimentos_user,
        'utilizador': user,
        # 'compras': compras,
        # 'ofertas': ofertas,
    }
    return render(
        request,
        'restau/pages/movimentos_compras_ofertas.html',
        context
    )
