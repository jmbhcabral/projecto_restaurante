# fidelidade/management/commands/reconciliar_movimentos_pontos.py

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from fidelidade.models import ComprasFidelidade, MovimentoPontos, OfertasFidelidade

User = get_user_model()


def saldo_old_system(user, fidelidade_id=None):
    """Saldo antigo usando expirado/processado."""
    compras = ComprasFidelidade.objects.filter(utilizador=user, expirado=False)
    ofertas = OfertasFidelidade.objects.filter(utilizador=user, processado=False)

    if fidelidade_id is not None:
        compras = compras.filter(fidelidade_id=fidelidade_id)
        ofertas = ofertas.filter(fidelidade_id=fidelidade_id)

    total_add = compras.aggregate(total=Sum("pontos_adicionados"))["total"] or 0
    total_sub = ofertas.aggregate(total=Sum("pontos_gastos"))["total"] or 0

    return total_add - total_sub


def saldo_ledger(user, fidelidade_id=None):
    """Saldo novo (ledger): créditos - débitos."""
    qs = MovimentoPontos.objects.filter(
        utilizador=user,
        status=MovimentoPontos.Status.CONFIRMADO
    )

    if fidelidade_id is not None:
        qs = qs.filter(fidelidade_id=fidelidade_id)

    creditos = qs.filter(
        tipo__in=[MovimentoPontos.Tipo.CREDITO, MovimentoPontos.Tipo.AJUSTE]
    ).aggregate(total=Sum("pontos"))["total"] or 0

    debitos = qs.filter(
        tipo__in=[MovimentoPontos.Tipo.DEBITO_RES, MovimentoPontos.Tipo.DEBITO_EXP]
    ).aggregate(total=Sum("pontos"))["total"] or 0

    return creditos - debitos


class Command(BaseCommand):
    help = "Reconcilia dados antigos criando DEBITO_EXP quando o saldo antigo != saldo ledger."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Aplica as correções (cria DEBITO_EXP). Sem isto é dry-run."
        )

    def handle(self, *args, **options):
        apply = options["apply"]

        self.stdout.write(self.style.WARNING(
            f"⚠️  A iniciar reconciliação (apply={apply})..."
        ))

        # Conjunto de pares (user, fidelidade) que têm alguma compra ou oferta
        pairs = set(
            list(ComprasFidelidade.objects.values_list("utilizador_id", "fidelidade_id")) +
            list(OfertasFidelidade.objects.values_list("utilizador_id", "fidelidade_id"))
        )

        total = len(pairs)
        self.stdout.write(f"🔎 A analisar {total} pares utilizador/fidelidade...")

        count_diff = 0
        count_applied = 0

        for idx, (user_id, fidelidade_id) in enumerate(pairs, start=1):
            if user_id is None or fidelidade_id is None:
                continue

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                continue

            old_balance = saldo_old_system(user, fidelidade_id)
            ledger_balance = saldo_ledger(user, fidelidade_id)

            diff = ledger_balance - old_balance

            if diff == 0:
                continue

            count_diff += 1

            self.stdout.write(
                f"[{idx}/{total}] user={user_id} fid={fidelidade_id} "
                f"old={old_balance} ledger={ledger_balance} diff={diff}"
            )

            if diff > 0 and apply:
                # Criar movimento DEBITO_EXP
                with transaction.atomic():
                    MovimentoPontos.objects.create(
                        utilizador=user,
                        fidelidade_id=fidelidade_id,
                        tipo=MovimentoPontos.Tipo.DEBITO_EXP,
                        status=MovimentoPontos.Status.CONFIRMADO,
                        pontos=diff,
                        criado_em=timezone.now(),
                    )
                count_applied += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  → Criado DEBITO_EXP de {diff} pontos."
                ))

            if diff < 0:
                self.stdout.write(self.style.WARNING(
                    "  ⚠️ Ledger tem MENOS pontos do que o sistema antigo. Rever manualmente."
                ))

        self.stdout.write(self.style.WARNING(
            f"🔍 {count_diff} pares com diferenças encontradas."
        ))
        if apply:
            self.stdout.write(self.style.SUCCESS(
                f"✅ {count_applied} DEBITO_EXP criados."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "⚠️  Sem alterações (modo dry-run). Use --apply para aplicar."
            ))