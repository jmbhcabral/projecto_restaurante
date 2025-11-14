# fidelidade/tasks.py
from celery import shared_task  # type: ignore
from django.apps import apps
from django.contrib.auth import get_user_model

from fidelidade.services import expirar_saldo_utilizador

User = get_user_model()


@shared_task
def expirar_pontos_inativos_task(dias_inatividade=45):
    """
    Task periódica que:
      - percorre utilizadores com movimentos no ledger
      - expira o saldo se já passou o prazo de inatividade
    É o equivalente Celery ao management command expirar_pontos_inativos.
    """
    MovimentoPontos = apps.get_model("fidelidade", "MovimentoPontos")

    user_ids = (
        MovimentoPontos.objects
        .exclude(utilizador_id=None)
        .values_list("utilizador_id", flat=True)
        .distinct()
    )

    total_users = len(user_ids)
    expirados = 0

    for idx, user_id in enumerate(user_ids, start=1):
        user = User.objects.filter(id=user_id).first()
        if not user:
            continue

        expirou = expirar_saldo_utilizador(user, dias_inatividade=dias_inatividade)
        if expirou:
            expirados += 1
            print(f"[{idx}/{total_users}] Expirado saldo do utilizador ID={user.pk}")

    print(
        f"✅ Task expirar_pontos_inativos_task concluída. "
        f"{expirados} utilizador(es) com saldo expirado."
    )