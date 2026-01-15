# djangoapp/perfil/services/profile_me_service.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from djangoapp.perfil.errors import CommonErrorCode, DomainError
from djangoapp.perfil.models import Perfil
from djangoapp.perfil.services.perfil_service import (
    ensure_perfil_business_defaults,
    refresh_address_capabilities,
)
from djangoapp.utils.model_validators import validar_nif

User = get_user_model()


@dataclass(frozen=True)
class ProfileMeUpdateResult:
    user_updated: list[str]
    perfil_updated: list[str]


def _validate_birthdate_change_rule(perfil: Perfil, new_date) -> None:
    # English comment: allow empty/None
    if new_date is None:
        return
    if perfil.data_nascimento == new_date:
        return

    last_changed_at = perfil.ultima_atualizacao_data_nascimento
    if last_changed_at:
        min_date = last_changed_at + timedelta(days=182.5)
        if timezone.now() < min_date:
            raise DomainError(
                code=CommonErrorCode.BAD_REQUEST,
                message="A data de nascimento só pode ser alterada após 6 meses.",
                http_status=400,
            )


def _ensure_phone_unique(perfil: Perfil, phone: str) -> None:
    phone = (phone or "").strip()
    if phone == "":
        return
    if Perfil.objects.filter(telemovel=phone).exclude(pk=perfil.pk).exists():
        raise DomainError(
            code=CommonErrorCode.BAD_REQUEST,
            message="Este número de telemóvel já está em uso.",
            http_status=400,
        )


@transaction.atomic
def update_me_profile(*, user: User, payload: dict[str, Any]) -> ProfileMeUpdateResult:
    """
    English comment:
    Update authenticated user's User + Perfil with central business rules.
    payload: {"user": {...}, "perfil": {...}}
    """
    perfil = (
        Perfil.objects
        .select_for_update()
        .filter(usuario=user)
        .first()
    )
    if not perfil:
        raise DomainError(
            code=CommonErrorCode.NOT_FOUND,
            message="Perfil não encontrado.",
            http_status=404,
        )

    # Keep business defaults consistent (numero_cliente, tipo_fidelidade, etc.)
    ensure_perfil_business_defaults(perfil)

    user_data = payload.get("user") or {}
    perfil_data = payload.get("perfil") or {}

    user_updated: set[str] = set()
    perfil_updated: set[str] = set()

    # -------------------------
    # Update User
    # -------------------------
    for field in ("first_name", "last_name"):
        if field in user_data:
            setattr(user, field, (user_data.get(field) or "").strip())
            user_updated.add(field)

    if user_updated:
        user.full_clean()
        user.save(update_fields=list(user_updated))

    # -------------------------
    # Business rules before update
    # -------------------------
    if "data_nascimento" in perfil_data:
        _validate_birthdate_change_rule(perfil, perfil_data.get("data_nascimento"))

    if "telemovel" in perfil_data:
        _ensure_phone_unique(perfil, perfil_data.get("telemovel") or "")

    # -------------------------
    # Update Perfil
    # -------------------------
    old_dob = perfil.data_nascimento

    editable_fields = (
        "data_nascimento",
        "telemovel",
        "nif",
        "notificacoes_email",
        "notificacoes_telemovel",
    )

    for field in editable_fields:
        if field in perfil_data:
            setattr(perfil, field, perfil_data.get(field))
            perfil_updated.add(field)

    # English comment: update DOB timestamp only if changed
    if "data_nascimento" in perfil_updated and perfil.data_nascimento != old_dob:
        perfil.ultima_atualizacao_data_nascimento = timezone.now()
        perfil_updated.add("ultima_atualizacao_data_nascimento")

    # English comment: derived flag based on real nif validation
    # (only update if nif was touched, otherwise leave as is)
    if "nif" in perfil_updated:
        perfil.has_valid_nif = bool(perfil.nif and validar_nif(perfil.nif))
        perfil_updated.add("has_valid_nif")

    if perfil_updated:
        try:
            perfil.full_clean()
            perfil.save(update_fields=list(perfil_updated))
        except IntegrityError:
            raise DomainError(
                code=CommonErrorCode.BAD_REQUEST,
                message="Este número de telemóvel já está em uso.",
                http_status=400,
            )

    # Refresh address flags (optional but keeps things correct if addresses changed elsewhere)
    refresh_address_capabilities(perfil)

    return ProfileMeUpdateResult(
        user_updated=sorted(user_updated),
        perfil_updated=sorted(perfil_updated),
    )