''' Este módulo contém as views para as operações de compra e oferta de pontos de fidelidade. '''

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from djangoapp.fidelidade.forms import ComprasFidelidadeForm, OfertasFidelidadeForm
from djangoapp.fidelidade.models import ComprasFidelidade
from djangoapp.fidelidade.services import registar_compra, registar_oferta
from djangoapp.perfil.views.perfil_api import send_push_notification
from djangoapp.utils.model_validators import (
    calcular_total_pontos,
    calcular_total_pontos_disponiveis,
)
from djangoapp.utils.scanner_input_interpreter import interpretar_dados

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

                                registar_compra(compra=compra_fidelidade)  

                                # Atualizar a última atividade do
                                # perfil(compra)
                                perfil = user.perfil
                                perfil.ultima_actividade = timezone.now()
                                perfil.save()

                                # Enviar notificação push para o utilizador
                                send_push_notification(user, 'Pontos adicionados', f'Compra registada com sucesso. Adicionou {compra_fidelidade.pontos_adicionados} pontos.')

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
            form = ComprasFidelidadeForm(
                request.POST, initial=initial_data)
            if form.is_valid():
                compra_fidelidade = form.save(commit=False)
                compra_fidelidade.utilizador = user
                compra_fidelidade.fidelidade = user.perfil.tipo_fidelidade
                compra_fidelidade.chave_g = '0'
                try:
                    compra_fidelidade.pontos_adicionados = round(
                        float(compra_fidelidade.compra) * compra_fidelidade.fidelidade.desconto / 100, 2)
                except (TypeError, ValueError) as e:
                    compra_fidelidade.pontos_adicionados = 0
                    logger.error(
                        "LOGGER: Erro ao calcular pontos adicionados: %s", e)
                    messages.error(
                        request, 'Erro ao calcular os pontos adicionados.')
                    
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
                
                return redirect('restau:compras_utilizador', utilizador_pk=utilizador_pk)
            else:
                messages.error(request, 'Erro ao processar a compra.')
                logger.warning("LOGGER: Erro ao processar a compra: %s", form.errors)
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


    total_pontos_disponiveis = calcular_total_pontos_disponiveis(user)
    total_pontos = calcular_total_pontos(user)

    initial_data = {
        'utilizador': user,
        'fidelidade': user.perfil.tipo_fidelidade.id,
    }


    if request.method == 'POST':
        form = OfertasFidelidadeForm(request.POST, initial=initial_data)

        if form.is_valid():
            ofertas = form.save(commit=False)
            
            if (ofertas.pontos_gastos is not None and ofertas.pontos_gastos > 0) and \
                    total_pontos_disponiveis >= ofertas.pontos_gastos:
                ofertas.utilizador = user
                ofertas.fidelidade = user.perfil.tipo_fidelidade
                ofertas.save()

                registar_oferta(oferta=ofertas)

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
