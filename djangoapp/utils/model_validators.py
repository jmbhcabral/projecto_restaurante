'''
Este módulo contém validadores de modelos personalizados para serem
usados em modelos de aplicações Django.
'''

from datetime import timedelta, datetime
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.db.models import Sum, F, Q, Max


def validate_png(image):
    if not image.name.lower().endswith('.png'):
        raise ValidationError('Imagem precisa ser .png')


def positive_price(value):
    if value < 0:
        raise ValidationError('O valor tem de ser positivo.')


def validar_nif(nif):
    # Remover espaços em branco e outros caracteres não numéricos
    nif = ''.join(filter(str.isdigit, nif))

    # Verificar se o NIF tem 9 dígitos após remover caracteres não numéricos
    if len(nif) != 9:
        return False

    # Converter o NIF para uma lista de inteiros
    nif_digitos = [int(digito) for digito in nif]

    # Verificar o dígito de controlo
    total = 0
    for i in range(8):
        total += nif_digitos[i] * (9 - i)

    resto = total % 11
    digito_controlo_calculado = 11 - resto if resto != 0 and resto != 1 else 0

    return digito_controlo_calculado == nif_digitos[8]


# Model ProdutoFidelidadeIndividual

def calcular_pontos(produto, fidelidade):
    ementa = fidelidade.ementa
    preco_field = ementa.nome_campo_preco_selecionado
    preco = getattr(produto, preco_field)
    if preco is None:
        raise ValueError(
            f'O produto {produto} não tem um preço definido no campo '
            f'{preco_field}'
        )
    preco_int = int(preco * 100)
    desconto = fidelidade.desconto
    pontos_necessarios = int(preco_int / (desconto / 100))
    return preco_int, pontos_necessarios


def verificar_expiracao_pontos(utilizador):
    '''Verificar se os pontos de fidelidade do utilizador expiraram'''

    # Importação dos modelos necessários
    from fidelidade.models import ComprasFidelidade, OfertasFidelidade

    # Obter a data da última compra feita pelo utilizador
    ultima_compra = ComprasFidelidade.objects.filter(utilizador=utilizador).aggregate(
        # Encontra a data mais recente da última compra
        ultima=models.Max('criado_em')
    )['ultima']

    # Obter a data da última oferta recebida pelo utilizador
    ultima_oferta = OfertasFidelidade.objects.filter(utilizador=utilizador).aggregate(
        # Encontra a data mais recente da última oferta
        ultima=models.Max('criado_em')
    )['ultima']

    # Função interna para garantir que as datas são timezone-aware
    def ensure_aware(datetime_obj):
        if datetime_obj is not None:  # Se a data não for nula
            # Verifica se a data não está ciente do fuso horário
            if timezone.is_naive(datetime_obj):
                # Converte para timezone-aware
                return timezone.make_aware(datetime_obj)
            return datetime_obj  # Se já for timezone-aware, retorna como está
        # Se a data for nula, retorna uma data mínima com fuso horário UTC
        return timezone.datetime.min.replace(tzinfo=timezone.utc)

    # Determina a última atividade do utilizador, considerando compras e ofertas
    ultima_atividade = max(
        # Converte a última compra para timezone-aware, se necessário
        ensure_aware(ultima_compra),
        # Converte a última oferta para timezone-aware, se necessário
        ensure_aware(ultima_oferta),
    )

    # Verifica se passaram mais de 30 dias desde a última atividade
    if timezone.now() - ultima_atividade > timedelta(days=45):
        print(f'Pontos expirados para {utilizador.username}')

        # Marca todas as compras anteriores à última atividade como expiradas
        ComprasFidelidade.objects.filter(
            utilizador=utilizador).update(expirado=True)

        # Marca todas as ofertas anteriores à última atividade como processadas
        OfertasFidelidade.objects.filter(
            utilizador=utilizador).update(processado=True)


def calcular_total_pontos(utilizador):
    '''Calcular o total de pontos de fidelidade disponíveis para um utilizador
    excepto os pontos adicionados hoje'''

    from fidelidade.models import ComprasFidelidade, OfertasFidelidade
    # Atualizar o estado dos pontos expirados
    verificar_expiracao_pontos(utilizador)

    # Calcular total de pontos adicionados que não estão expirados
    total_pontos_adicionados = ComprasFidelidade\
        .objects\
        .filter(utilizador=utilizador, expirado=False)\
        .aggregate(total=Sum('pontos_adicionados'))['total'] or 0

    # Calcular total de pontos gastos que não estão expirados
    total_pontos_gastos = OfertasFidelidade\
        .objects\
        .filter(utilizador=utilizador, processado=False)\
        .aggregate(total=Sum('pontos_gastos'))['total'] or 0

    # O saldo de pontos disponíveis será o total de pontos adicionados
    # menos o total de pontos gastos
    total_pontos = total_pontos_adicionados - total_pontos_gastos

    return total_pontos


def calcular_total_pontos_disponiveis(user):
    '''Calcular o total de pontos de fidelidade disponíveis para um utilizador
    exluindo os pontos adicionados hoje'''

    from fidelidade.models import ComprasFidelidade

    total_pontos = calcular_total_pontos(user)

    hoje = timezone.now()

    # Calcular total de pontos adicionados hoje
    total_pontos_adicionados_hoje = ComprasFidelidade\
        .objects\
        .filter(utilizador=user, criado_em__date=hoje.date())\
        .aggregate(total=Sum('pontos_adicionados'))['total'] or 0

    # calcular total de pontos disponiveis
    total_pontos_disponiveis = total_pontos - total_pontos_adicionados_hoje

    return total_pontos_disponiveis


def calcular_pontos_expirados(user):
    '''Calcular o total de pontos expirados para um utilizador'''

    from fidelidade.models import ComprasFidelidade, OfertasFidelidade

    todos_pontos_expirados = ComprasFidelidade\
        .objects\
        .filter(utilizador=user, expirado=True)\
        .aggregate(total=Sum('pontos_adicionados'))['total'] or 0

    total_ofertas_processadas = OfertasFidelidade\
        .objects\
        .filter(utilizador=user, processado=True)\
        .aggregate(total=Sum('pontos_gastos'))['total'] or 0

    total_pontos_expirados = todos_pontos_expirados - total_ofertas_processadas

    return total_pontos_expirados


def processar_transacoes_existentes():
    '''Processar todas as transações existentes para todos os perfis de utilizadores'''

    from fidelidade.models import ComprasFidelidade, OfertasFidelidade
    from perfil.models import Perfil
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Max

    # Iterar sobre todos os perfis de utilizadores
    for perfil in Perfil.objects.all():
        # Obter a última compra ou oferta existente (a mais recente)
        ultima_compra = ComprasFidelidade.objects.filter(
            utilizador=perfil.usuario).aggregate(
            ultima=Max('criado_em')
        )['ultima']

        ultima_oferta = OfertasFidelidade.objects.filter(
            utilizador=perfil.usuario).aggregate(
            ultima=Max('criado_em')
        )['ultima']

        # Determinar a última atividade válida apenas se houver transações
        ultima_atividade = max(ultima_compra, ultima_oferta) if (
            ultima_compra or ultima_oferta) else None

        print(f'Perfil: {perfil.usuario.username}')
        print(f'Última atividade calculada: {ultima_atividade}')

        # Combinar todas as transações (compras e ofertas) ordenadas por data
        transacoes = sorted(
            list(ComprasFidelidade.objects.filter(utilizador=perfil.usuario)) +
            list(OfertasFidelidade.objects.filter(utilizador=perfil.usuario)),
            key=lambda x: x.criado_em
        )

        # Inicializar a data da última transação verificada
        ultima_transacao = None

        # Iterar sobre todas as transações do utilizador
        for transacao in transacoes:
            if ultima_transacao is None:
                ultima_transacao = transacao.criado_em
                continue

            # Verificar se houve inatividade de mais de 45 dias
            dias_inativos = (transacao.criado_em - ultima_transacao).days
            print(
                f'Comparando {transacao.criado_em} com {ultima_transacao} - Dias inativos: {dias_inativos}')

            if dias_inativos > 45:
                print(
                    f'Inatividade de mais de 45 dias detectada: {dias_inativos} dias.')
                # Expirar todas as transações anteriores à transação atual
                for t in transacoes:
                    if t.criado_em < transacao.criado_em:
                        if isinstance(t, ComprasFidelidade):
                            if not t.expirado:
                                t.expirado = True
                                t.save()
                                print(
                                    f'Transação de compra expirada: {t.criado_em}')
                        elif isinstance(t, OfertasFidelidade):
                            if not t.processado:
                                t.processado = True
                                t.save()
                                print(
                                    f'Transação de oferta processada: {t.criado_em}')

            # Atualizar a última transação verificada
            ultima_transacao = transacao.criado_em

        # Após processar todas as transações, atualizar o campo ultima_actividade no perfil
        perfil.ultima_actividade = ultima_atividade
        perfil.save()

        print(
            f'Processamento concluído para o perfil: {perfil.usuario.username}')
        print('---')
