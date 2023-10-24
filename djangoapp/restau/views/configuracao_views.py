from django.shortcuts import render, redirect
from restau.models import (
    ActiveSetup, ImagemLogo, ImagemTopo, Intro, IntroImagem, FraseCima,
    ImagemFraseCima, FraseInspiradora, FraseBaixo, ImagemFraseBaixo,
    ImagemPadrao, ContactosSite, GoogleMaps, Horario
)
from typing import Dict
from django.contrib import messages


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

    contacto = ContactosSite.objects.all().first()

    active_setup = ActiveSetup.objects.first()

    if request.method == 'POST':
        if active_setup:
            contactos_para_activar = ContactosSite.objects.all().first()
            active_setup.active_contactos_site = contactos_para_activar
            active_setup.save()
            messages.success(
                request,
                'Contactos Ativados com sucesso!'
            )
            return redirect(
                'restau:contatos_site',
            )

        else:
            messages.error(
                request,
                'Não existe uma configuração ativa!'
            )

    context = {
        'contacto': contacto,
    }

    return render(
        request,
        'restau/pages/contatos_site.html',
        context,
    )


def google_maps(request):

    local = GoogleMaps.objects.all().first()

    active_setup = ActiveSetup.objects.first()

    if request.method == 'POST':
        if active_setup:
            mapa_para_activar = GoogleMaps.objects.all().first()
            active_setup.active_google_maps = mapa_para_activar
            active_setup.save()
            messages.success(
                request,
                'Mapa Ativado com sucesso!'
            )
            return redirect(
                'restau:google_maps',
            )

        else:
            messages.error(
                request,
                'Não existe uma configuração ativa!'
            )

    context = {
        'local': local,
    }

    return render(
        request,
        'restau/pages/google_maps.html',
        context,
    )


def horario(request):

    horarios = Horario.objects.all().order_by('id')
    numero_horarios = len(horarios)

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

    active_setup = ActiveSetup.objects.first()

    if request.method == 'POST':
        horarios_para_activar = Horario.objects.all()
        active_setup.active_horario.set(horarios_para_activar)

    context = {
        'horarios_ordenados': horarios_ordenados,
        'numero_horarios': numero_horarios,
    }

    return render(
        request,
        'restau/pages/horario.html',
        context,
    )
