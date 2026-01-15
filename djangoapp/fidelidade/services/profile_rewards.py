# djangoapp/fidelidade/services/profile_rewards.py
from __future__ import annotations

from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone

from djangoapp.fidelidade.constants import PROFILE_COMPLETED_BONUS
from djangoapp.fidelidade.models import MovimentoPontos
from djangoapp.perfil.models import Perfil


def _is_profile_complete(perfil: Perfil) -> bool:
    user = perfil.usuario
    return all([
        bool((user.first_name or "").strip()),
        bool((user.last_name or "").strip()),
        bool((perfil.telemovel or "").strip()),
        bool(perfil.data_nascimento),
    ])


@transaction.atomic
def try_award_profile_completed_bonus(perfil_id: int, pontos: Decimal = Decimal("1")) -> bool:
    """
    Tries to award a one-time bonus when the profile becomes complete.
    Returns True if awarded, False otherwise.
    """
    perfil = (
        Perfil.objects
        .select_for_update()
        .select_related("usuario", "tipo_fidelidade")
        .get(id=perfil_id)
    )

    if not perfil.tipo_fidelidade:
        return False

    if not _is_profile_complete(perfil):
        return False

    try:
        MovimentoPontos.objects.create(
            utilizador=perfil.usuario,
            fidelidade=perfil.tipo_fidelidade,
            tipo=MovimentoPontos.Tipo.CREDITO,
            status=MovimentoPontos.Status.CONFIRMADO,
            pontos=pontos,
            code=PROFILE_COMPLETED_BONUS,
            criado_em=timezone.now(),
        )
        return True

    except IntegrityError:
        # UniqueConstraint hit -> already awarded
        return False