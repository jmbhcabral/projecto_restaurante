# djangoapp/fidelidade/services/ledger_service.py

from djangoapp.fidelidade.models import (
    ComprasFidelidade,
    OfertasFidelidade,
)


def get_user_default_fidelidade(utilizador):
    """Return the user's most recent loyalty program."""
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