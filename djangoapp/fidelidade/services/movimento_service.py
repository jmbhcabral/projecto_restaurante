# djangoapp/fidelidade/services/movimento_service.py
from __future__ import annotations

from django.utils import timezone

from djangoapp.fidelidade.models import (
    ComprasFidelidade,
    MovimentoPontos,
    OfertasFidelidade,
)


def registar_compra(compra: ComprasFidelidade) -> None:
    """Register a credit movement for a loyalty purchase."""
    MovimentoPontos.objects.create(
        utilizador=compra.utilizador,
        fidelidade=compra.fidelidade,
        tipo="CREDITO",
        pontos=compra.pontos_adicionados,
        status="CONFIRMADO",
        criado_em=timezone.now(),
    )


def registar_oferta(oferta: OfertasFidelidade) -> None:
    """Register a debit movement for a redeemed offer."""
    MovimentoPontos.objects.create(
        utilizador=oferta.utilizador,
        fidelidade=oferta.fidelidade,
        tipo="DEBITO_RES",
        pontos=oferta.pontos_gastos,
        status="CONFIRMADO",
        criado_em=timezone.now(),
    )