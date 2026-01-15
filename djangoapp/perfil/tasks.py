""" Este módulo contém as tarefas para o aplicativo de perfil. """
# djangoapp/perfil/tasks.py
from __future__ import annotations

from celery import shared_task
from django.core.management import call_command


@shared_task(bind=True, name="djangoapp.perfil.tasks.cleanup_verification_codes")
def cleanup_verification_codes_task(self, days: int = 30) -> dict[str, int]:
    """
    Runs the management command that deletes old verification codes.
    """
    # call_command returns None, so we return something useful for logs/monitoring
    call_command("cleanup_verification_codes", days=days)
    return {"days": days}