from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from restau.models import (
    ActiveSetup, ImagemLogo, ImagemTopo, Intro
)
from restau.forms import (
    ImagemLogoForm, LogosFormSet, ImagemTopoForm, TopoFormSet, IntroForm,
    IntroFormSet
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


def criar_logo(request):
    form_action = reverse('restau:criar_logo')
    if request.method == 'POST':
        form = ImagemLogoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Logo adicionado com sucesso!'
            )
    else:
        form = ImagemLogoForm()

    context = {
        'form_action': form_action,  # 'restau:criar_logo
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_logo.html',
        context,
    )


def apagar_logo(request, ):

    form_action = reverse('restau:apagar_logo')
    if request.method == 'POST':
        formset = LogosFormSet(
            request.POST,
            request.FILES,
            queryset=ImagemLogo.objects.all()
        )

        if formset.is_valid():
            delete_flag = False
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    if 'DELETE' in form.changed_data:
                        delete_flag = True
                        messages.success(
                            request, 'Logotipo apagado com sucesso!')
                    else:
                        instance.save()

            if delete_flag:
                for form in formset:
                    if 'DELETE' in form.changed_data:
                        instance = form.instance
                        instance.delete()

            return redirect('restau:imagem_logo')

    else:
        formset = LogosFormSet(queryset=ImagemLogo.objects.all())

    context = {
        'form_action': form_action,  # 'restau:apagar_logo
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/apagar_logo.html',
        context,
    )


def escolher_logo(request,):

    form_action = reverse('restau:escolher_logo')

    if request.method == 'POST':
        print('request.POST: ', request.POST)

        imagem_id = request.POST.get('imagem_id', None)
        print('imagem_id: ', imagem_id)

        if imagem_id:
            ImagemLogo.objects.update(is_visible=False)
            ImagemLogo.objects.filter(id=imagem_id).update(is_visible=True)

            messages.success(
                request, 'Logo escolhido com sucesso!')
            return redirect('restau:imagem_logo')

    imagens = ImagemLogo.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_logo
        'imagens': imagens,
    }

    return render(
        request,
        'restau/pages/escolher_logo.html',
        context,
    )


def criar_imagem_topo(request):
    form_action = reverse('restau:criar_imagem_topo')
    if request.method == 'POST':
        form = ImagemTopoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'imagem adicionada com sucesso!'
            )
    else:
        form = ImagemTopoForm()

    context = {
        'form_action': form_action,  # 'restau:criar_imagem_topo
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_imagem_topo.html',
        context,
    )


def apagar_imagem_topo(request, ):

    form_action = reverse('restau:apagar_imagem_topo')
    if request.method == 'POST':
        formset = TopoFormSet(
            request.POST,
            request.FILES,
            queryset=ImagemTopo.objects.all()
        )

        if formset.is_valid():
            delete_flag = False
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    if 'DELETE' in form.changed_data:
                        delete_flag = True
                        messages.success(
                            request, 'Imagem(s) apagada(s) com sucesso!')
                    else:
                        instance.save()

            if delete_flag:
                for form in formset:
                    if 'DELETE' in form.changed_data:
                        instance = form.instance
                        instance.delete()

            return redirect('restau:imagem_Topo')

    else:
        formset = TopoFormSet(queryset=ImagemTopo.objects.all())

    context = {
        'form_action': form_action,  # 'restau:apagar_imagem_topo
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/apagar_imagem_topo.html',
        context,
    )


def escolher_imagem_topo(request,):

    form_action = reverse('restau:escolher_imagem_topo')

    if request.method == 'POST':
        print('request.POST: ', request.POST)

        imagem_id = request.POST.get('imagem_id', None)
        print('imagem_id: ', imagem_id)

        if imagem_id:
            ImagemTopo.objects.update(is_visible=False)
            ImagemTopo.objects.filter(id=imagem_id).update(is_visible=True)

            messages.success(
                request, 'Imagem escolhida com sucesso!')
            return redirect('restau:imagem_topo')

    imagens = ImagemTopo.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_imagem_topo
        'imagens': imagens,
    }

    return render(
        request,
        'restau/pages/escolher_imagem_topo.html',
        context,
    )


def criar_intro(request):
    form_action = reverse('restau:criar_intro')
    if request.method == 'POST':
        form = IntroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Texto adicionado com sucesso!'
            )
    else:
        form = IntroForm()

    context = {
        'form_action': form_action,  # 'restau:criar_intro
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_intro.html',
        context,
    )


def apagar_intro(request, ):

    form_action = reverse('restau:apagar_intro')
    if request.method == 'POST':
        formset = IntroFormSet(
            request.POST,
            request.FILES,
            queryset=Intro.objects.all()
        )

        if formset.is_valid():
            delete_flag = False
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    if 'DELETE' in form.changed_data:
                        delete_flag = True
                        messages.success(
                            request, 'Intro(s) apagado(s) com sucesso!')
                    else:
                        instance.save()

            if delete_flag:
                for form in formset:
                    if 'DELETE' in form.changed_data:
                        instance = form.instance
                        instance.delete()

            return redirect('restau:intro')

    else:
        formset = IntroFormSet(queryset=Intro.objects.all())

    context = {
        'form_action': form_action,  # 'restau:apagar_intro
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/apagar_intro.html',
        context,
    )


def escolher_intro(request,):

    form_action = reverse('restau:escolher_intro')

    if request.method == 'POST':
        print('request.POST: ', request.POST)

        imagem_id = request.POST.get('imagem_id', None)
        print('imagem_id: ', imagem_id)

        if imagem_id:
            Intro.objects.update(is_visible=False)
            Intro.objects.filter(id=imagem_id).update(is_visible=True)

            messages.success(
                request, 'Imagem escolhida com sucesso!')
            return redirect('restau:intro')

    imagens = Intro.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_intro
        'imagens': imagens,
    }

    return render(
        request,
        'restau/pages/escolher_intro.html',
        context,
    )
