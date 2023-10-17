from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from restau.models import ActiveSetup, ImagemLogo
from restau.forms import (
    ImagemLogoForm, LogosFormSet
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
                            request, 'Foto apagada com sucesso!')
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
        'form_action': form_action,  # 'restau:criar_logo
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
        formset = LogosFormSet(
            request.POST,
            request.FILES,
            queryset=ImagemLogo.objects.all()
        )

        if formset.is_valid():
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    if 'visivel' in form.changed_data:
                        instance.visivel = True
                        instance.save()
                    else:
                        instance.visivel = False
                        instance.save()

            return redirect('restau:imagem_logo')

    else:
        formset = LogosFormSet(queryset=ImagemLogo.objects.all())

    context = {
        'form_action': form_action,  # 'restau:escolher_visivel
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/escolher_logo.html',
        context,
    )
