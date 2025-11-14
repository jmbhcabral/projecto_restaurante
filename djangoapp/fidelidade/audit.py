# fidelidade/audit.py
from django.db.models import Sum

from fidelidade.models import ComprasFidelidade, MovimentoPontos, OfertasFidelidade


def saldo_old_system(utilizador, fidelidade=None):
    """
    Saldo pelo modelo antigo:
    - compras NÃO expiradas
    - ofertas NÃO processadas (no teu código atual)
    """
    compras_qs = ComprasFidelidade.objects.filter(utilizador=utilizador, expirado=False)
    ofertas_qs = OfertasFidelidade.objects.filter(utilizador=utilizador, processado=False)

    if fidelidade is not None:
        compras_qs = compras_qs.filter(fidelidade=fidelidade)
        ofertas_qs = ofertas_qs.filter(fidelidade=fidelidade)

    total_add = compras_qs.aggregate(total=Sum("pontos_adicionados"))["total"] or 0
    total_spent = ofertas_qs.aggregate(total=Sum("pontos_gastos"))["total"] or 0

    return total_add - total_spent


def saldo_ledger(utilizador, fidelidade=None):
    """
    Saldo pelo ledger:
    (CREDITO + AJUSTE) - (DEBITO_RES + DEBITO_EXP)
    """
    qs = MovimentoPontos.objects.filter(
        utilizador=utilizador,
        status=MovimentoPontos.Status.CONFIRMADO,
    )
    if fidelidade is not None:
        qs = qs.filter(fidelidade=fidelidade)

    creditos = (
        qs.filter(tipo__in=[MovimentoPontos.Tipo.CREDITO, MovimentoPontos.Tipo.AJUSTE])
        .aggregate(total=Sum("pontos"))
        .get("total")
        or 0
    )

    debitos = (
        qs.filter(tipo__in=[MovimentoPontos.Tipo.DEBITO_RES, MovimentoPontos.Tipo.DEBITO_EXP])
        .aggregate(total=Sum("pontos"))
        .get("total")
        or 0
    )

    return creditos - debitos