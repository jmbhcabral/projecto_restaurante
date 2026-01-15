# djangoapp/perfil/services/onboarding_optional.py
from __future__ import annotations

from djangoapp.perfil.models import Perfil

OPTIONAL_FIELDS = (
    "first_name",
    "last_name",
    "telemovel",
    "data_nascimento",
)


def optional_fields_state(perfil: Perfil) -> dict[str, bool]:
    """
    Return per-field completion state for optional onboarding.
    """
    user = perfil.usuario

    return {
        "first_name": bool((user.first_name or "").strip()),
        "last_name": bool((user.last_name or "").strip()),
        "telemovel": bool((perfil.telemovel or "").strip()),
        "data_nascimento": bool(perfil.data_nascimento),
    }


def optional_missing_fields(perfil: Perfil) -> list[str]:
    state = optional_fields_state(perfil)
    return [field for field in OPTIONAL_FIELDS if not state.get(field)]


def calc_optional_progress(perfil: Perfil) -> int:
    """
    Compute optional onboarding progress percentage.
    """
    state = optional_fields_state(perfil)
    total = len(OPTIONAL_FIELDS)
    filled = sum(1 for field in OPTIONAL_FIELDS if state.get(field))

    return int((filled / total) * 100)


def is_optional_complete(perfil: Perfil) -> bool:
    return calc_optional_progress(perfil) == 100


def should_show_optional_banner(perfil: Perfil) -> bool:
    """
    Decide whether optional onboarding banner should be shown.
    """
    if not perfil.onboarding_required_completed:
        return False
    if perfil.onboarding_optional_completed:
        return False

    # English comment: if fields are incomplete, show banner
    return bool(optional_missing_fields(perfil))