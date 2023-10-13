from django.shortcuts import render, redirect
from django.urls import reverse
from restau.models import Fotos


def galeria(request):
    fotos = Fotos.objects.all()
    if fotos:
        print(f'fotos: {fotos}')
    else:
        print('fotos: None')

    context = {
        'fotos': fotos,
    }

    return render(
        request,
        'restau/pages/galeria.html',
        context
    )
