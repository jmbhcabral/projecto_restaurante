from django.shortcuts import render
from restau.models import (
    ActiveSetup, ImagemLogo, ImagemTopo, Intro
)
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


def imagem_topo(request):
    def grouper(iterable, n, fillvalue=None):
        # "Coleta dados em grupos fixos"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    imagens = ImagemTopo.objects.all().order_by('id')
    imagens_grouped = list(grouper(imagens, 5))
    if imagens:
        for group in imagens_grouped:
            for imagem in group:
                if imagem:
                    imagem.imagem.name = basename(imagem.imagem.name)

    context = {
        'imagens': imagens,
        'imagens_grouped': imagens_grouped,
    }

    return render(
        request,
        'restau/pages/imagem_topo.html',
        context,
    )


def intro(request):
    def grouper(iterable, n, fillvalue=None):
        # "Coleta dados em grupos fixos"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    textos = Intro.objects.all().order_by('id')
    textos_grouped = list(grouper(textos, 5))
    # if textos:
    #     for group in textos_grouped:
    #         for texto in group:
    #             if texto:
    #                 texto.texto.name = basename(texto.texto.name)

    context = {
        'textos': textos,
        'textos_grouped': textos_grouped,
    }

    return render(
        request,
        'restau/pages/intro.html',
        context,
    )
