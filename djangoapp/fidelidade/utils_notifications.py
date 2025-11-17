import calendar
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from perfil.models import Perfil

from fidelidade.ledger import get_expiry_date, get_ledger_balance
from fidelidade.models import MovimentoPontos

DIAS_INATIVIDADE_EXPIRAR_PONTOS = 45


def _q_aniversario_para_data_efetiva(date):
    """
    Dada uma data 'date' (já no ano atual), devolve um Q() que:
    - apanha todos os perfis cujo aniversário 'cai' nesse dia
    - num ano não bissexto, 28/02 inclui também nascidos a 29/02
    """
    base_q = Q(
        data_nascimento__isnull=False,
        data_nascimento__day=date.day,
        data_nascimento__month=date.month,
    )

    # Caso especial:
    # - se estivermos num ano NÃO bissexto
    # - e estivermos a considerar 28/02
    #   → incluir também quem nasceu a 29/02
    if not calendar.isleap(date.year) and date.month == 2 and date.day == 28:
        base_q = base_q | Q(
            data_nascimento__isnull=False,
            data_nascimento__day=29,
            data_nascimento__month=2,
        )

    return base_q


def obter_aniversarios_para_notificar():
    """
    Devolve dois QuerySets:
    - perfis_aniversario_hoje: fazem 'anos' hoje (considerando 29/02 → 28/02 em anos normais)
    - perfis_aniversario_m8: fazem 'anos' daqui a 8 dias (mesma lógica)
    """
    today = timezone.localdate()

    # 1) hoje
    qs_hoje = Perfil.objects.filter(_q_aniversario_para_data_efetiva(today))

    # 2) daqui a 8 dias
    target_minus_8 = today + timedelta(days=8)
    qs_m8 = Perfil.objects.filter(_q_aniversario_para_data_efetiva(target_minus_8))

    return qs_hoje, qs_m8

def obter_utilizadores_pontos_a_expirar():
    today = timezone.localdate()

    users = User.objects.filter(is_active=True)

    result = []

    for user in users:

        last_movement = MovimentoPontos.objects.filter(
            utilizador=user,
            tipo='CREDITO',
            status='CONFIRMADO',
        ).order_by('-criado_em').first()

        if not last_movement:
            continue

        balance = get_ledger_balance(user)
        if balance <= 0:
            continue

        expiration_date = get_expiry_date(user)
        if not expiration_date:
            continue
        remaining_days = (expiration_date - today).days
        if remaining_days <= 0:
            continue

        result.append({
            'user': user,
            'balance': balance,
            'expiration_date': expiration_date,
            'remaining_days': remaining_days,
        })

    print(result)

    return result