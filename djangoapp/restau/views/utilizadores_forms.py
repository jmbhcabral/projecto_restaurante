''' Este módulo contém as views para as operações de compra e oferta de pontos de fidelidade. '''

import logging
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from fidelidade.forms import ComprasFidelidadeForm, OfertasFidelidadeForm
from fidelidade.models import ComprasFidelidade, OfertasFidelidade
from django.db import models, IntegrityError
from django.utils import timezone
from utils.scanner_input_interpreter import interpretar_dados
from utils.model_validators import (
    calcular_total_pontos, calcular_total_pontos_disponiveis
)

logger = logging.getLogger(__name__)


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def compras_utilizador(request, utilizador_pk):
    user = get_object_or_404(User, id=utilizador_pk)

    initial_data = {
        'utilizador': user,
        'fidelidade': user.perfil.tipo_fidelidade.id,
        'qr_data': '',
    }

    if request.method == 'POST':
        qr_data = request.POST.get('dados', '')
        if qr_data:
            if len(qr_data) > 20:
                try:
                    dados_qr = interpretar_dados(qr_data)
                    valor_compra = dados_qr.get('O', '')
                    chave_g_valor = dados_qr.get('G', '')

                    if not valor_compra or not chave_g_valor:
                        messages.error(
                            request, 'Erro ao ler Qrcode.')
                        logger.warning(
                            "LOGGER: Erro ao ler Qrcode, valor: %s, chave G: %s", valor_compra, chave_g_valor)

                    # Verificar se a chave G já foi usada
                    elif ComprasFidelidade.objects\
                        .filter(chave_g=chave_g_valor)\
                            .exists():
                        messages.error(
                            request, 'Uma compra com este código já foi registada.')
                        logger.warning(
                            "LOGGER: Compra duplicada para chave G: %s", chave_g_valor)
                    else:
                        form = ComprasFidelidadeForm(
                            request.POST, initial=initial_data)
                        if form.is_valid():
                            compra_fidelidade = form.save(commit=False)
                            compra_fidelidade.utilizador = user
                            compra_fidelidade.fidelidade = user.perfil.tipo_fidelidade
                            compra_fidelidade.compra = valor_compra if valor_compra else 0
                            compra_fidelidade.chave_g = chave_g_valor if chave_g_valor else ''

                            try:
                                compra_fidelidade.pontos_adicionados = round(
                                    float(compra_fidelidade.compra) * compra_fidelidade.fidelidade.desconto / 100, 2)
                            except (TypeError, ValueError) as e:
                                compra_fidelidade.pontos_adicionados = 0
                                logger.error(
                                    "LOGGER: Erro ao calcular pontos adicionados: %s", e)
                                messages.error(
                                    request, 'Erro ao calcular os pontos adicionados.')

                            try:
                                compra_fidelidade.save()

                                # Atualizar a última atividade do
                                # perfil(compra)
                                perfil = user.perfil
                                perfil.ultima_actividade = timezone.now()
                                perfil.save()

                                logger.info(
                                    'LOGGER: Compra registada com sucesso.')
                                messages.success(
                                    request, 'Compra registada com sucesso.')
                            except IntegrityError as e:
                                messages.error(
                                    request, 'Uma compra com este código já foi registada.')
                                logger.error(
                                    "LOGGER: Tentativa de registrar compra duplicada para chave G: %s - %s", chave_g_valor, e)

                except Exception as e:
                    logger.error("LOGGER: Erro ao processar dados QR: %s", e)
                    messages.error(
                        request, 'Erro ao processar os dados do QR.')
            else:
                messages.error(request, 'Erro ao ler o código QR.')
                logger.warning("LOGGER: Código QR inválido: %s", qr_data)
        return redirect('restau:compras_utilizador', utilizador_pk=utilizador_pk)
    else:
        form = ComprasFidelidadeForm(initial=initial_data)

    context = {
        'form': form,
        'utilizador': user,
        'perfil': user.perfil,
    }

    return render(request, 'restau/pages/compras_utilizador.html', context)


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def ofertas_utilizador(request, utilizador_id):
    user = get_object_or_404(User, id=utilizador_id)

    # agora = timezone.now()
    # inicio_do_dia_atual = agora.replace(
    #     hour=0, minute=0, second=0, microsecond=0)
    # inicio_para_uso_de_pontos = agora.replace(
    #     hour=11, minute=30, second=0, microsecond=0)

    # if agora < inicio_para_uso_de_pontos:
    #     data_de_referencia = inicio_do_dia_atual - timezone.timedelta(days=1)
    # else:
    #     data_de_referencia = inicio_do_dia_atual

    # pontos_ganhos = ComprasFidelidade.objects.filter(
    #     utilizador=user, criado_em__lt=data_de_referencia).aggregate(
    #     total_pontos_ganhos=models.Sum('pontos_adicionados'))

    # pontos_gastos = OfertasFidelidade.objects.filter(
    #     utilizador=user).aggregate(
    #     total_pontos_gastos=models.Sum('pontos_gastos'))

    # pontos_ganhos_decimal = pontos_ganhos['total_pontos_ganhos'] or 0
    # pontos_gastos_decimal = pontos_gastos['total_pontos_gastos'] or 0

    # total_pontos_disponiveis = pontos_ganhos_decimal - pontos_gastos_decimal

    total_pontos_disponiveis = calcular_total_pontos_disponiveis(user)
    total_pontos = calcular_total_pontos(user)

    initial_data = {
        'utilizador': user,
        'fidelidade': user.perfil.tipo_fidelidade.id,
    }

    # pontos_ganhos_totais = ComprasFidelidade.objects.filter(
    #     utilizador=user).aggregate(
    #     total_pontos_ganhos=models.Sum('pontos_adicionados'))

    # pontos_gastos_totais = OfertasFidelidade.objects.filter(
    #     utilizador=user).aggregate(
    #     total_pontos_gastos=models.Sum('pontos_gastos'))

    # total_pontos_ganhos_decimal = pontos_ganhos_totais['total_pontos_ganhos'] or 0
    # total_pontos_gastos_decimal = pontos_gastos_totais['total_pontos_gastos'] or 0

    # total_pontos = total_pontos_ganhos_decimal - total_pontos_gastos_decimal

    if request.method == 'POST':
        form = OfertasFidelidadeForm(request.POST, initial=initial_data)

        if form.is_valid():
            ofertas = form.save(commit=False)
            if ofertas.pontos_gastos is not None and \
                    total_pontos_disponiveis >= ofertas.pontos_gastos:
                ofertas.utilizador = user
                ofertas.fidelidade = user.perfil.tipo_fidelidade
                ofertas.save()

                # Atualizar a última atividade do perfil(oferta)
                perfil = user.perfil
                perfil.ultima_actividade = timezone.now()
                perfil.save()

                messages.success(
                    request,
                    'Oferta registada com sucesso.'
                )
                return redirect(
                    'restau:admin_utilizadores'
                )
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
        'fidelidade': user.perfil.tipo_fidelidade,
    }

    return render(request, 'restau/pages/ofertas_utilizador.html', context)
