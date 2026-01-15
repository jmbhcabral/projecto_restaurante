""" Este módulo contém os sinais para o perfil do utilizador. """
# djangoapp/perfil/signals.py
from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from djangoapp.perfil.models import Morada, Perfil
from djangoapp.perfil.services.perfil_service import (
    ensure_perfil_business_defaults,
    refresh_address_capabilities,
)
from djangoapp.perfil.services.qr_service import ensure_qr_code


@receiver(post_save, sender=Perfil)
def perfil_post_save(sender, instance: Perfil, created: bool, **kwargs):
    """
    1) Garante defaults do negócio (numero_cliente, tipo_fidelidade, etc.)
    2) Gera QR code (1x) quando aplicável
    """
    # Evitar loops: services fazem save(update_fields=...) e isto volta a disparar.
    # Estratégia: só agir quando created ou quando faltam coisas essenciais.
    if created or not instance.numero_cliente:
        ensure_perfil_business_defaults(instance)

    # QR: só quando tiver numero_cliente e qr_code vazio
    ensure_qr_code(instance)


@receiver(post_save, sender=Morada)
def morada_post_save(sender, instance: Morada, **kwargs):
    """
    Sempre que uma morada muda, atualizamos flags do Perfil.
    """
    try:
        perfil = instance.usuario.perfil
    except Perfil.DoesNotExist:
        return
    refresh_address_capabilities(perfil)