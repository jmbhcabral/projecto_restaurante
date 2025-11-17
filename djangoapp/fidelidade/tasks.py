# fidelidade/tasks.py   

from datetime import timedelta

from celery import shared_task  # type: ignore
from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils import timezone
from utils.notifications import send_push_notification

from fidelidade.models import NotificacaoAutomatica
from fidelidade.services import expirar_saldo_utilizador
from fidelidade.services_notificacoes import send_email_notification
from fidelidade.utils_notifications import (
    obter_aniversarios_para_notificar,
    obter_utilizadores_pontos_a_expirar,
)

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

@shared_task
def enviar_avisos_aniversario_task():
    """
    Task periódica que:
      - envia avisos de aniversário para utilizadores
    """
    today = timezone.localdate()
    perfis_today, perfis_m8 = obter_aniversarios_para_notificar()

    # 1) 8 dias antes - sugestão de festa
    for perfil in perfis_m8:
        user = perfil.usuario
        #data de referencia = data real do aniversário (hoje + 8 dias)
        data_ref = today + timedelta(days=8)
        dias_ate_aniversario = 8

        # evitar duplicados
        if NotificacaoAutomatica.objects.filter(
            user=user,
            tipo='birthday_minus_8',
            referencia_data=data_ref,
        ).exists():
            continue

        # Email de notificação
        send_email_notification(
            to=user.email,
            subject="Planeia já a tua festa de aniversário na Hamburgueria Extreme Way 🎉",
            template_name="emails/aniversario_minus_8.html",
            context={
                "nome": user.first_name or user.username,
                "data_aniversario": data_ref,
                "dias_ate_aniversario": dias_ate_aniversario,
            },
        )

        # Notificação push
        send_push_notification(
            user=user,
            title="Falta pouco para o teu aniversário 🎂",
            body="Garante já a tua reserva para a festa na Hamburgueria Extreme Way!",
            data={"tipo": "birthday_minus_8"},
        )

        NotificacaoAutomatica.objects.create(
            user=user, tipo="birthday_minus_8", referencia_data=data_ref
        )

    # 2) Dia do aniversário
    for perfil in perfis_today:
        user = perfil.usuario
        data_ref = today

        # evitar duplicados
        if NotificacaoAutomatica.objects.filter(
            user=user, tipo="birthday_day", referencia_data=data_ref,
        ).exists():
            continue

        # Email de notificação
        send_email_notification(
            to=user.email,
            subject="Parabéns! 🎉 A equipa Extreme Way deseja-te um excelente aniversário",
            template_name="emails/aniversario_dia.html",
            context={
                "nome": user.first_name or user.username,
                "data_aniversario": data_ref,
            },
        )

        # Notificação push
        send_push_notification(
            user=user,
            title="Parabéns! 🎂",
            body="Passa por cá hoje e celebra o teu dia connosco!",
            data={"tipo": "birthday_day"},
        )

        NotificacaoAutomatica.objects.create(
            user=user, tipo="birthday_day", referencia_data=data_ref
        )


def enviar_avisos_pontos_a_expirar_task():
    """
    Task periódica que:
      - envia avisos de pontos a expirar para utilizadores
    """
    # today = timezone.localdate()
    users = obter_utilizadores_pontos_a_expirar()

    for item in users:
        user = item['user']
        balance = item['balance']
        expiration_date = item['expiration_date']
        remaining_days = item['remaining_days']

        if remaining_days not in [15, 7, 1]:
            continue

        # mapear tipo de notificação
        tipo_map ={
            15: 'points_minus_15',
            7: 'points_minus_7',
            1: 'points_minus_1',
        }
        tipo = tipo_map[remaining_days]

        # evitar duplicados
        if NotificacaoAutomatica.objects.filter(
            user=user, tipo=tipo, referencia_data=expiration_date,
        ).exists():
            continue

        # Mensagens diferentes conforme a proximidade da expiração
        if remaining_days == 15:
            subject = 'Tens pontos a expirar em 15 dias ✨'
        elif remaining_days == 7:
            subject = 'Última semana para usar os teus pontos 🔥'

        else:
            subject = 'Último dia para usar os teus pontos ⏱️'
        
        # Email de notificação
        send_email_notification(
            to=user.email,
            subject=subject,
            template_name="emails/pontos_a_expirar.html",
            context={
                "nome": user.first_name or user.username,
                "balance": balance,
                "expiration_date": expiration_date,
                "remaining_days": remaining_days,
            },
        )

        # Notificação push
        send_push_notification(
            user=user,
            title=subject,
            body=f"Tens {balance} pontos que expiram em {remaining_days} dia(s). Aproveita!",
            data={
                "tipo": tipo,
                "remaining_days": remaining_days,
                "expiration_date": str(expiration_date),
            },
        )

        NotificacaoAutomatica.objects.create(
            user=user, tipo=tipo, referencia_data=expiration_date
        )