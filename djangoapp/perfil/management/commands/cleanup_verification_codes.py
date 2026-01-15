""" Este módulo contém o comando para limpar os códigos de verificação expirados. """
# djangoapp/perfil/management/commands/cleanup_verification_codes.py
from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from djangoapp.perfil.models import VerificationCode


class Command(BaseCommand):
    help = "Delete old verification codes (expired/used) to keep table small."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Delete records older than this many days (default: 30).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print counts only, do not delete anything.",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        days: int = options["days"]
        dry_run: bool = options["dry_run"]

        cutoff = timezone.now() - timedelta(days=days)

        qs_expired_old = VerificationCode.objects.filter(expires_at__lt=cutoff)
        qs_used_old = VerificationCode.objects.filter(used_at__isnull=False, used_at__lt=cutoff)

        expired_count = qs_expired_old.count()
        used_count = qs_used_old.count()

        self.stdout.write(self.style.NOTICE(f"Cutoff: {cutoff.isoformat()}"))
        self.stdout.write(self.style.NOTICE(f"Expired old: {expired_count}"))
        self.stdout.write(self.style.NOTICE(f"Used old: {used_count}"))

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run enabled: no deletions performed."))
            return

        deleted_used = qs_used_old.delete()[0]
        deleted_expired = qs_expired_old.delete()[0]

        self.stdout.write(self.style.SUCCESS(f"Deleted expired: {deleted_expired}"))
        self.stdout.write(self.style.SUCCESS(f"Deleted used: {deleted_used}"))