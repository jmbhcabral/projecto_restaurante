from django.shortcuts import render
from restau.models import Fotos


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
