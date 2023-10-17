from django.shortcuts import render
from restau.models import ActiveSetup, ImagemLogo
from itertools import zip_longest
from os.path import basename


def configuracao(request):
    campos = ActiveSetup.objects.all()

    context = {
        'campos': campos,
    }

    return render(
        request,
        'restau/pages/configuracao.html',
        context,
    )


def imagem_logo(request):
    def grouper(iterable, n, fillvalue=None):
        # "Coleta dados em grupos fixos"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    logos = ImagemLogo.objects.all().order_by('id')
    logos_grouped = list(grouper(logos, 5))
    if logos:
        for group in logos_grouped:
            for logo in group:
                if logo:
                    logo.imagem.name = basename(logo.imagem.name)

    context = {
        'logos': logos,
        'logos_grouped': logos_grouped,
    }

    return render(
        request,
        'restau/pages/logos.html',
        context,
    )
