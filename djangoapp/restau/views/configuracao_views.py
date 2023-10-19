from django.shortcuts import render
from restau.models import (
    ActiveSetup, ImagemLogo, ImagemTopo, Intro, IntroImagem, FraseCima,
    ImagemFraseCima, FraseInspiradora, FraseBaixo, ImagemFraseBaixo,
    ImagemPadrao, ContactosSite
)


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

    logos = ImagemLogo.objects.all().order_by('id')
    numero_logos = len(logos)

    context = {
        'logos': logos,
        'numero_logos': numero_logos,
    }

    return render(
        request,
        'restau/pages/logos.html',
        context,
    )


def imagem_topo(request):

    imagens = ImagemTopo.objects.all().order_by('id')
    numero_imagens = len(imagens)

    context = {
        'imagens': imagens,
        'numero_imagens': numero_imagens,
    }

    return render(
        request,
        'restau/pages/imagem_topo.html',
        context,
    )


def intro(request):

    textos = Intro.objects.all().order_by('id')
    numero_textos = len(textos)

    context = {
        'numero_textos': numero_textos,
        'textos': textos,
    }

    return render(
        request,
        'restau/pages/intro.html',
        context,
    )


def intro_imagem(request):

    imagens = IntroImagem.objects.all().order_by('id')
    numero_imagens = len(imagens)

    context = {
        'imagens': imagens,
        'numero_imagens': numero_imagens,
    }

    return render(
        request,
        'restau/pages/intro_imagem.html',
        context,
    )


def frase_cima(request):

    textos = FraseCima.objects.all().order_by('id')
    numero_textos = len(textos)

    context = {
        'numero_textos': numero_textos,
        'textos': textos,
    }

    return render(
        request,
        'restau/pages/frase_cima.html',
        context,
    )


def imagem_frase_cima(request):

    imagens = ImagemFraseCima.objects.all().order_by('id')
    numero_imagens = len(imagens)

    context = {
        'imagens': imagens,
        'numero_imagens': numero_imagens,
    }

    return render(
        request,
        'restau/pages/imagem_frase_cima.html',
        context,
    )


def frase_central(request):

    textos = FraseInspiradora.objects.all().order_by('id')
    numero_textos = len(textos)

    context = {
        'numero_textos': numero_textos,
        'textos': textos,
    }

    return render(
        request,
        'restau/pages/frase_central.html',
        context,
    )


def frase_baixo(request):

    textos = FraseBaixo.objects.all().order_by('id')
    numero_textos = len(textos)

    context = {
        'numero_textos': numero_textos,
        'textos': textos,
    }

    return render(
        request,
        'restau/pages/frase_baixo.html',
        context,
    )


def imagem_frase_baixo(request):

    imagens = ImagemFraseBaixo.objects.all().order_by('id')
    numero_imagens = len(imagens)

    context = {
        'imagens': imagens,
        'numero_imagens': numero_imagens,
    }

    return render(
        request,
        'restau/pages/imagem_frase_baixo.html',
        context,
    )


def imagem_padrao(request):

    imagens = ImagemPadrao.objects.all().order_by('id')
    numero_imagens = len(imagens)

    context = {
        'imagens': imagens,
        'numero_imagens': numero_imagens,
    }

    return render(
        request,
        'restau/pages/imagem_padrao.html',
        context,
    )


def contatos_site(request):

    contatos = ContactosSite.objects.all().order_by('id')
    numero_contatos = len(contatos)

    context = {
        'contatos': contatos,
        'numero_contatos': numero_contatos,
    }

    return render(
        request,
        'restau/pages/contatos_site.html',
        context,
    )
