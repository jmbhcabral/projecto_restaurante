from django.db import transaction
from django.utils import timezone

from djangoapp.fidelidade.ledger import get_days_to_expiry, get_ledger_balance
from djangoapp.fidelidade.models import (
    ComprasFidelidade,
    MovimentoPontos,
    OfertasFidelidade,
)


def registar_compra(compra: ComprasFidelidade):
    MovimentoPontos.objects.create(
        utilizador=compra.utilizador,
        fidelidade=compra.fidelidade,
        tipo="CREDITO",
        pontos=compra.pontos_adicionados,
        status="CONFIRMADO",
        criado_em=timezone.now(),
    )

def registar_oferta(oferta: OfertasFidelidade):
    MovimentoPontos.objects.create(
        utilizador=oferta.utilizador,
        fidelidade=oferta.fidelidade,
        tipo="DEBITO_RES",
        pontos=oferta.pontos_gastos,
        status="CONFIRMADO",
        criado_em=timezone.now(),
    )

def get_user_default_fidelidade(utilizador):
    compra = (
        ComprasFidelidade.objects
        .filter(utilizador=utilizador)
        .order_by("-criado_em")
        .first()
    )
    if compra:
        return compra.fidelidade

    oferta = (
        OfertasFidelidade.objects
        .filter(utilizador=utilizador)
        .order_by("-criado_em")
        .first()
    )
    if oferta:
        return oferta.fidelidade

    return None

def expirar_saldo_utilizador(utilizador, dias_inatividade=45):
    saldo_atual = get_ledger_balance(utilizador)
    if saldo_atual <= 0:
        return False

    dias_para_expirar = get_days_to_expiry(utilizador, dias_inatividade=dias_inatividade)
    if dias_para_expirar is None:
        return False

    if dias_para_expirar > 0:
        return False

    fidelidade = get_user_default_fidelidade(utilizador)
    if fidelidade is None:
        return False

    with transaction.atomic():
        MovimentoPontos.objects.create(
            utilizador=utilizador,
            fidelidade=fidelidade,
            tipo="DEBITO_EXP",
            status="CONFIRMADO",
            pontos=saldo_atual,
            criado_em=timezone.now(),
        )

    return True