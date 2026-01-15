# djangoapp/perfil/services/onboarding_optional.py
from __future__ import annotations

from djangoapp.perfil.models import Perfil

OPTIONAL_FIELDS_TOTAL = 4


def calc_optional_progress(perfil: Perfil) -> int:
    # English comment: compute progress based on required optional fields
    user = perfil.usuario

    filled = 0
    if (user.first_name or "").strip():
        filled += 1
    if (user.last_name or "").strip():
        filled += 1
    if (perfil.telemovel or "").strip():
        filled += 1
    if perfil.data_nascimento is not None:
        filled += 1

    return int((filled / OPTIONAL_FIELDS_TOTAL) * 100)


def is_optional_complete(perfil: Perfil) -> bool:
    return calc_optional_progress(perfil) == 100