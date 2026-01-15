# djangoapp/fidelidade/services/expiracao_service.py

from django.db import transaction
from django.utils import timezone

from djangoapp.fidelidade.ledger import (
    get_days_to_expiry,
    get_ledger_balance,
)
from djangoapp.fidelidade.models import MovimentoPontos
from djangoapp.fidelidade.services.ledger_service import (
    get_user_default_fidelidade,
)


def expirar_saldo_utilizador(utilizador, dias_inatividade: int = 45) -> bool:
    """Expire user's loyalty balance after inactivity period."""
    saldo_atual = get_ledger_balance(utilizador)
    if saldo_atual <= 0:
        return False

    dias_para_expirar = get_days_to_expiry(
        utilizador,
        dias_inatividade=dias_inatividade,
    )
    if dias_para_expirar is None or dias_para_expirar > 0:
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