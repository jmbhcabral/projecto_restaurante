# fidelidade/ledger.py
from datetime import timedelta
from typing import TYPE_CHECKING, cast

from django.apps import apps
from django.db.models import Max, Sum
from django.utils import timezone

if TYPE_CHECKING:
    from fidelidade.models import MovimentoPontos


def _get_movimento_model():
    """
    Evita import circular: em vez de `from fidelidade.models import MovimentoPontos`,
    usamos apps.get_model.
    """
    return apps.get_model("fidelidade", "MovimentoPontos")


def get_ledger_balance(utilizador, fidelidade=None):
    """
    Saldo de pontos baseado apenas no ledger:
    (CREDITO + AJUSTE) - (DEBITO_RES + DEBITO_EXP)
    """
    MovimentoPontos = _get_movimento_model()

    qs = MovimentoPontos.objects.filter(
        utilizador=utilizador,
        status="CONFIRMADO",
    )
    if fidelidade is not None:
        qs = qs.filter(fidelidade=fidelidade)

    creditos = (
        qs.filter(tipo__in=["CREDITO", "AJUSTE"])
        .aggregate(total=Sum("pontos"))
        .get("total")
        or 0
    )

    debitos = (
        qs.filter(tipo__in=["DEBITO_RES", "DEBITO_EXP"])
        .aggregate(total=Sum("pontos"))
        .get("total")
        or 0
    )

    return creditos - debitos


def get_today_credited_points(utilizador, fidelidade=None):
    """
    Pontos adicionados HOJE (movimentos CREDITO).
    Equivalente aos pontos indisponíveis do sistema antigo.
    """
    MovimentoPontos = _get_movimento_model()
    hoje = timezone.localdate()

    qs = MovimentoPontos.objects.filter(
        utilizador=utilizador,
        status="CONFIRMADO",
        tipo="CREDITO",
        criado_em__date=hoje,
    )
    if fidelidade is not None:
        qs = qs.filter(fidelidade=fidelidade)

    return qs.aggregate(total=Sum("pontos"))["total"] or 0


def get_available_points(utilizador, fidelidade=None):
    """
    Pontos disponíveis para usar:
    saldo total - pontos ganhos hoje.
    """
    saldo_total = get_ledger_balance(utilizador, fidelidade=fidelidade)
    hoje_indisponivel = get_today_credited_points(utilizador, fidelidade=fidelidade)
    return saldo_total - hoje_indisponivel


def get_last_purchase_dt(utilizador, fidelidade=None):
    """
    Última compra relevante para expiração.
    (movimentos de tipo CREDITO)
    """
    MovimentoPontos = _get_movimento_model()

    qs = MovimentoPontos.objects.filter(
        utilizador=utilizador,
        status="CONFIRMADO",
        tipo="CREDITO",
    )
    if fidelidade is not None:
        qs = qs.filter(fidelidade=fidelidade)

    return qs.aggregate(last=Max("criado_em"))["last"]


def get_expiry_date(utilizador, dias_inatividade=45, fidelidade=None):
    """
    Data em que expira o saldo por inatividade.
    """
    last = get_last_purchase_dt(utilizador, fidelidade=fidelidade)
    if not last:
        return None

    last_date = timezone.localtime(last).date()
    return last_date + timedelta(days=dias_inatividade)


def get_days_to_expiry(utilizador, dias_inatividade=45, fidelidade=None):
    """
    Número de dias até os pontos expirarem.
    """
    expiry_date = get_expiry_date(utilizador, dias_inatividade, fidelidade)
    if not expiry_date:
        return None

    today = timezone.localdate()
    return (expiry_date - today).days

def get_movimentos_pontos(utilizador):
    """
    Lista de movimentos de pontos para um utilizador.
    """
    MovimentoPontos = _get_movimento_model()
    qs = MovimentoPontos.objects.filter(
        utilizador=utilizador,
        status="CONFIRMADO",
        tipo__in=["CREDITO", "DEBITO_RES", "DEBITO_EXP", "AJUSTE"],
    ).order_by("-criado_em")

    movimentos = []
    for movimento_raw in qs:
        movimento = cast("MovimentoPontos", movimento_raw)
        tipo_display = movimento.get_tipo_display()  # type: ignore[attr-defined]
        criado_em_local = timezone.localtime(movimento.criado_em)
        disponivel_amanha = timezone.localdate() <= criado_em_local.date() if movimento.tipo == 'CREDITO' else False
        expirado = movimento.tipo == 'DEBITO_EXP'
        pontos = float(movimento.pontos)
        movimentos.append({
            'data': criado_em_local.strftime('%Y-%m-%d'),
            'tipo': tipo_display,
            'pontos': '-' + str(pontos) if movimento.tipo == 'DEBITO_EXP' or movimento.tipo == 'DEBITO_RES' else pontos,
            'cor': 'orange' if disponivel_amanha else 'red' if expirado else 'green' if movimento.tipo == 'CREDITO' else 'blue',
            'disponivel_amanha': disponivel_amanha,
            'expirado': expirado,
        })
    return movimentos