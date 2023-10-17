from django.shortcuts import render
from restau.models import ActiveSetup, ImagemLogo
from itertools import zip_longest


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
    print('Count: ', logos.count())
    for logo in logos:
        print('imagem_name: ', logo.imagem.name)
        print('imagem_url: ', logo.imagem.url)
    context = {
        'logos': logos,
        'logos_grouped': logos_grouped,
    }

    return render(
        request,
        'restau/pages/logos.html',
        context,
    )
