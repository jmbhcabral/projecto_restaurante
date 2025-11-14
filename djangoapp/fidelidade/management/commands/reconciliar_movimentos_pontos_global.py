# fidelidade/management/commands/reconciliar_movimentos_pontos_global.py

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from fidelidade.models import ComprasFidelidade, MovimentoPontos, OfertasFidelidade

User = get_user_model()


def saldo_old_system_global(user):
    """
    Saldo antigo GLOBAL (todas as fidelidades):
    - compras NÃO expiradas
    - ofertas NÃO processadas
    """
    total_add = (ComprasFidelidade.objects
                 .filter(utilizador=user, expirado=False)
                 .aggregate(total=Sum("pontos_adicionados"))["total"] or 0)

    total_sub = (OfertasFidelidade.objects
                 .filter(utilizador=user, processado=False)
                 .aggregate(total=Sum("pontos_gastos"))["total"] or 0)

    return total_add - total_sub


def saldo_ledger_global(user):
    """
    Saldo ledger GLOBAL (todas as fidelidades):
    (CREDITO + AJUSTE) - (DEBITO_RES + DEBITO_EXP)
    """
    qs = MovimentoPontos.objects.filter(
        utilizador=user,
        status=MovimentoPontos.Status.CONFIRMADO,
    )

    creditos = (qs.filter(
        tipo__in=[MovimentoPontos.Tipo.CREDITO, MovimentoPontos.Tipo.AJUSTE]
    ).aggregate(total=Sum("pontos"))["total"] or 0)

    debitos = (qs.filter(
        tipo__in=[MovimentoPontos.Tipo.DEBITO_RES, MovimentoPontos.Tipo.DEBITO_EXP]
    ).aggregate(total=Sum("pontos"))["total"] or 0)

    return creditos - debitos


def get_user_fidelidade_for_expiration(user):
    """
    Escolhe uma fidelidade para associar ao DEBITO_EXP global.
    Estratégia simples: primeira fidelidade onde o user tem movimentos.
    """
    compra = (ComprasFidelidade.objects
              .filter(utilizador=user)
              .select_related("fidelidade")
              .first())
    if compra:
        return compra.fidelidade.pk

    oferta = (OfertasFidelidade.objects
              .filter(utilizador=user)
              .select_related("fidelidade")
              .first())
    if oferta:
        return oferta.fidelidade.pk

    # fallback: None (em princípio não deve acontecer se só chamarmos para users com movimentos)
    return None


class Command(BaseCommand):
    help = "Reconcilia o saldo do ledger com o saldo antigo ao nível GLOBAL de utilizador, criando DEBITO_EXP se necessário."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Aplica as correções (cria DEBITO_EXP). Sem isto é apenas dry-run."
        )

    def handle(self, *args, **options):
        apply = options["apply"]

        self.stdout.write(self.style.WARNING(
            f"⚠️  A iniciar reconciliação GLOBAL (por utilizador) (apply={apply})..."
        ))

        # users que têm pelo menos uma compra ou oferta
        user_ids = set(
            list(ComprasFidelidade.objects.values_list("utilizador_id", flat=True)) +
            list(OfertasFidelidade.objects.values_list("utilizador_id", flat=True))
        )
        user_ids.discard(None)

        total = len(user_ids)
        self.stdout.write(f"🔎 A analisar {total} utilizadores...")

        count_diff = 0
        count_applied = 0

        for idx, user_id in enumerate(user_ids, start=1):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                continue

            old_balance = saldo_old_system_global(user)
            ledger_balance = saldo_ledger_global(user)
            diff = ledger_balance - old_balance

            if diff == 0:
                continue

            count_diff += 1
            self.stdout.write(
                f"[{idx}/{total}] user={user_id} old={old_balance} "
                f"ledger={ledger_balance} diff={diff}"
            )

            if diff > 0 and apply:
                fidelidade_id = get_user_fidelidade_for_expiration(user)
                if not fidelidade_id:
                    self.stdout.write(self.style.WARNING(
                        "  ⚠️ Sem fidelidade associada, a ignorar este user."
                    ))
                    continue

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
                    f"  → Criado DEBITO_EXP global de {diff} pontos."
                ))

            if diff < 0:
                self.stdout.write(self.style.WARNING(
                    "  ⚠️ diff < 0 (ledger com MENOS pontos que o sistema antigo). "
                    "Rever manualmente este user antes de fazer AJUSTE."
                ))

        self.stdout.write(self.style.WARNING(
            f"🔍 {count_diff} utilizadores com diferenças."
        ))
        if apply:
            self.stdout.write(self.style.SUCCESS(
                f"✅ {count_applied} DEBITO_EXP globais criados."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "⚠️  Nenhuma alteração feita (dry-run). Use --apply para aplicar."
            ))