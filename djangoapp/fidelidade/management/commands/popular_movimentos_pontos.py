from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from djangoapp.fidelidade.models import (
    ComprasFidelidade,
    MovimentoPontos,
    OfertasFidelidade,
)

BATCH_SIZE = 500


class Command(BaseCommand):
    help = "Popula a tabela MovimentoPontos a partir de ComprasFidelidade e OfertasFidelidade (dados históricos)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-first",
            action="store_true",
            help="Apaga todos os MovimentoPontos antes de popular (usar com cuidado).",
        )

    def handle(self, *args, **options):
        clear_first = options["clear_first"]

        self.stdout.write(self.style.WARNING("⚠️  Início da migração para MovimentoPontos..."))

        if clear_first:
            self._clear_movimentos()

        with transaction.atomic():
            self._migrar_compras()
            self._migrar_ofertas()

        self.stdout.write(self.style.SUCCESS("✅ Migração concluída."))

    def _clear_movimentos(self):
        total = MovimentoPontos.objects.count()
        self.stdout.write(self.style.WARNING(f"  → A apagar {total} movimentos existentes..."))
        MovimentoPontos.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("  → Movimentos apagados."))

    def _migrar_compras(self):
        qs = (
            ComprasFidelidade.objects
            .select_related("fidelidade", "utilizador")
            .order_by("id")
        )
        total = qs.count()
        self.stdout.write(self.style.WARNING(f"🧾 A migrar {total} compras..."))

        movimentos_batch = []
        processed = 0

        for compra in qs.iterator(chunk_size=BATCH_SIZE):
            if not compra.utilizador:
                continue
            if compra.pontos_adicionados is None:
                continue

            movimentos_batch.append(
                MovimentoPontos(
                    utilizador=compra.utilizador,
                    fidelidade=compra.fidelidade,
                    tipo=MovimentoPontos.Tipo.CREDITO,
                    status=MovimentoPontos.Status.CONFIRMADO,
                    pontos=compra.pontos_adicionados,
                    compra=compra,
                    criado_em=compra.criado_em or timezone.now(),
                )
            )

            if len(movimentos_batch) >= BATCH_SIZE:
                MovimentoPontos.objects.bulk_create(movimentos_batch)
                processed += len(movimentos_batch)
                self.stdout.write(f"  → {processed}/{total} compras migradas...")
                movimentos_batch = []

        if movimentos_batch:
            MovimentoPontos.objects.bulk_create(movimentos_batch)
            processed += len(movimentos_batch)
            self.stdout.write(f"  → {processed}/{total} compras migradas (final).")

    def _migrar_ofertas(self):
        qs = (
            OfertasFidelidade.objects
            .select_related("fidelidade", "utilizador")
            .order_by("id")
        )
        total = qs.count()
        self.stdout.write(self.style.WARNING(f"🎁 A migrar {total} ofertas..."))

        movimentos_batch = []
        processed = 0

        for oferta in qs.iterator(chunk_size=BATCH_SIZE):
            if not oferta.utilizador:
                continue
            if oferta.pontos_gastos is None:
                continue

            movimentos_batch.append(
                MovimentoPontos(
                    utilizador=oferta.utilizador,
                    fidelidade=oferta.fidelidade,
                    tipo=MovimentoPontos.Tipo.DEBITO_RES,
                    status=MovimentoPontos.Status.CONFIRMADO,
                    pontos=oferta.pontos_gastos,
                    oferta=oferta,
                    criado_em=oferta.criado_em or timezone.now(),
                )
            )

            if len(movimentos_batch) >= BATCH_SIZE:
                MovimentoPontos.objects.bulk_create(movimentos_batch)
                processed += len(movimentos_batch)
                self.stdout.write(f"  → {processed}/{total} ofertas migradas...")
                movimentos_batch = []

        if movimentos_batch:
            MovimentoPontos.objects.bulk_create(movimentos_batch)
            processed += len(movimentos_batch)
            self.stdout.write(f"  → {processed}/{total} ofertas migradas (final).")