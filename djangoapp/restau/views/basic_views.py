from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from restau.models import ActiveSetup, Fotos, Horario
from typing import Dict


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def admin_home(request):

    return render(
        request,
        'restau/pages/admin_home.html',


    )


def index(request):

    galeria = Fotos.objects \
        .all() \
        .order_by('ordem') \


    active_setup = ActiveSetup.objects.get()

    horarios = Horario.objects.all()

    dict_horarios: Dict[str, int] = {
        'Segunda': 1,
        'Terça': 2,
        'Quarta': 3,
        'Quinta': 4,
        'Sexta': 5,
        'Sábado': 6,
        'Domingo': 7,
        'Feriados': 8,
    }

    horarios_ordenados = sorted(
        horarios,
        key=lambda x: dict_horarios.get(x.dia_semana, 0),  # type: ignore
    )

    return render(
        request,
        'restau/pages/index.html',
        {'active_setup': active_setup,
         'galeria': galeria,
         'horarios_ordenados': horarios_ordenados,
         },
    )


def programa_fidelidade(request):

    active_setup = ActiveSetup.objects.get()

    return render(
        request,
        'restau/pages/programa_fidelidade.html',
        {'active_setup': active_setup,
         },
    )
