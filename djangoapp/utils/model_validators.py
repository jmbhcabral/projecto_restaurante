"""
Este módulo contém validadores de modelos personalizados para serem
usados em modelos de aplicações Django.
"""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone


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


# -------------------------------------------------------------------
# Model ProdutoFidelidadeIndividual - esta parte mantemos como estava
# -------------------------------------------------------------------

def calcular_pontos(produto, fidelidade):
    """
    Mantém o comportamento antigo: calcula pontos com base no preço.
    Não depende do ledger.
    """
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


# -------------------------------------------------------------------
# ⚠️ Funções de pontos - mantemos os nomes, mas agora usam o ledger
# -------------------------------------------------------------------

def verificar_expiracao_pontos(utilizador, dias_inatividade=45):
    """
    DEPRECATED para cálculo de saldo.
    Mantido apenas por compatibilidade se for chamado algures.
    A expiração real passa a ser feita via ledger (DEBITO_EXP).
    """

    from djangoapp.perfil.models import Perfil

    try:
        perfil = Perfil.objects.get(usuario=utilizador)
    except Perfil.DoesNotExist:
        perfil = None

    if perfil and perfil.ultima_actividade:
        last = perfil.ultima_actividade.date()
        expiry_date = last + timedelta(days=dias_inatividade)
        today = timezone.localdate()
        days_left = (expiry_date - today).days
    else:
        expiry_date = None
        days_left = None

    return {
        "expired": False,
        "expiry_date": expiry_date,
        "days_left": days_left,
        "reason": "ledger_driven",
    }


def calcular_total_pontos(utilizador):
    """
    Calcular o total de pontos de fidelidade disponíveis para um utilizador.
    ANTES: via ComprasFidelidade/OfertasFidelidade.
    AGORA: via ledger, mas mantém assinatura e nome.
    """
    from djangoapp.fidelidade.ledger import get_ledger_balance

    return get_ledger_balance(utilizador)


def calcular_total_pontos_disponiveis(user):
    """
    Calcular o total de pontos disponíveis excluindo os pontos ganhos hoje.
    ANTES: recalculava diretamente nas tabelas antigas.
    AGORA: delega no ledger.
    """
    from djangoapp.fidelidade.ledger import get_available_points

    return get_available_points(user)


def calcular_pontos_indisponiveis(user):
    """
    Calcular o total de pontos indisponíveis (ganhos hoje).
    ANTES: somava ComprasFidelidade de hoje.
    AGORA: usa o ledger (CREDITO de hoje).
    """
    from djangoapp.fidelidade.ledger import get_today_credited_points

    return get_today_credited_points(user)


def calcular_pontos_expirados(user):
    """
    Calcular o total de pontos expirados para um utilizador.
    Versão ledger: soma todos os DEBITO_EXP confirmados.
    """
    from django.apps import apps

    MovimentoPontos = apps.get_model("fidelidade", "MovimentoPontos")

    total_expirado = (
        MovimentoPontos.objects.filter(
            utilizador=user,
            tipo="DEBITO_EXP",
            status="CONFIRMADO",
        ).aggregate(total=Sum("pontos"))["total"] or 0
    )

    return total_expirado


def calcular_dias_para_expirar(user):
    """
    Calcular quantos dias faltam para os pontos expirarem.
    Agora delega para o ledger (get_days_to_expiry).
    """
    from djangoapp.fidelidade.ledger import get_days_to_expiry

    return get_days_to_expiry(user, dias_inatividade=45)


def processar_transacoes_existentes():
    """
    Função antiga que mexia em expirado/processado nas tabelas antigas.
    Agora o ledger gere expiração via DEBITO_EXP, por isso esta função
    fica vazia para evitar efeitos colaterais.
    """
    return