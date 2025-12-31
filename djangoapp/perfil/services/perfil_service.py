""" Este módulo contém os serviços para o perfil do utilizador. """
# djangoapp/perfil/services/perfil_service.py
from __future__ import annotations

from dataclasses import dataclass

from django.db import connection, transaction
from django.utils import timezone

from djangoapp.perfil.models import Morada, Perfil

SEQ_NAME = "perfil_numero_cliente_seq"


@dataclass(frozen=True)
class CustomerNumberResult:
    numero_cliente: str
    seq_value: int


def allocate_customer_number() -> CustomerNumberResult:
    """
    Gera número de cliente via Postgres sequence (concurrency-safe).
    """
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT nextval('{SEQ_NAME}')")
        seq_value = int(cursor.fetchone()[0])

    # Mantemos o teu formato CEW-XXXX
    numero_cliente = f"CEW-{seq_value}"
    return CustomerNumberResult(numero_cliente=numero_cliente, seq_value=seq_value)


@transaction.atomic
def ensure_perfil_business_defaults(perfil: Perfil) -> Perfil:
    """
    Garante invariantes do negócio que DEVEM existir no Perfil.
    """
    updated = False

    # Numero de cliente (seguro)
    if not perfil.numero_cliente:
        res = allocate_customer_number()
        perfil.numero_cliente = res.numero_cliente
        updated = True

    # Tipo fidelidade derivado do estudante (barato e determinístico)
    expected_tipo = perfil.estudante.tipo_fidelidade if perfil.estudante else None
    if perfil.tipo_fidelidade_id != (expected_tipo.id if expected_tipo else None):
        perfil.tipo_fidelidade = expected_tipo
        updated = True

    # Flags capabilities (derivadas)
    has_nif = bool(perfil.nif)
    perfil.has_valid_nif = bool(perfil.nif)  # validação “real” é no serializer/form
    # se quiseres só marcar true se nif for válido, faz isso no serializer e grava no perfil.
    updated = True if perfil.has_valid_nif != has_nif else updated

    if updated:
        perfil.updated_at = timezone.now()
        perfil.save(update_fields=[
            "numero_cliente",
            "tipo_fidelidade",
            "has_valid_nif",
            "updated_at",
        ])

    return perfil


@transaction.atomic
def refresh_address_capabilities(perfil: Perfil) -> None:
    """
    Mantém flags has_delivery_address / has_billing_address coerentes com a DB.
    """
    user_id = perfil.usuario_id

    has_delivery = Morada.objects.filter(usuario_id=user_id, purpose=Morada.Purpose.DELIVERY, is_active=True).exists()
    has_billing = Morada.objects.filter(usuario_id=user_id, purpose=Morada.Purpose.BILLING, is_active=True).exists()

    changed = False
    if perfil.has_delivery_address != has_delivery:
        perfil.has_delivery_address = has_delivery
        changed = True
    if perfil.has_billing_address != has_billing:
        perfil.has_billing_address = has_billing
        changed = True

    if changed:
        perfil.save(update_fields=["has_delivery_address", "has_billing_address"])