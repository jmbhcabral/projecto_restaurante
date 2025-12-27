from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from djangoapp.restau.models import Fotos


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def galeria(request):
    numero_fotos = Fotos.objects.all().count()
    fotos = Fotos.objects.all()
    if fotos:
        print(f'fotos: {fotos}')
    else:
        print('fotos: None')

    context = {
        'numero_fotos': numero_fotos,
        'fotos': fotos,
    }

    return render(
        request,
        'restau/pages/galeria.html',
        context
    )
