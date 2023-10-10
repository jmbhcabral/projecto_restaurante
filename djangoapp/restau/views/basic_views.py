from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from restau.models import FrontendSetup, ActiveSetup


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def admin_home(request):

    return render(
        request,
        'restau/pages/admin_home.html',


    )


def index(request):
    main_logo = FrontendSetup.objects \
        .filter(imagem_logo__isnull=False) \
        .order_by('-id') \
        .first()

    main_image = FrontendSetup.objects \
        .filter(imagem_topo__isnull=False) \
        .order_by('-id') \
        .first()

    return render(
        request,
        'restau/pages/index.html',
        {'main_logo': main_logo,
         'main_image': main_image},
    )
