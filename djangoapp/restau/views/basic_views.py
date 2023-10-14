from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from restau.models import ActiveSetup, Fotos


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


    active_setup = ActiveSetup.objects \
        .select_related(
            'active_imagem_logo', 'active_imagem_topo',
            'active_intro', 'active_frase_inspiradora', 'active_frase_cima',
            'active_frase_baixo') \
        .all() \
        .first()

    return render(
        request,
        'restau/pages/index.html',
        {'active_setup': active_setup,
         'galeria': galeria
         },
    )
