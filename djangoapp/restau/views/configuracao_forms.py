from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse

from restau.models import (
    ActiveSetup, ImagemLogo, ImagemTopo, Intro, IntroImagem, FraseCima,
    ImagemFraseCima, FraseInspiradora, FraseBaixo, ImagemFraseBaixo,
    ImagemPadrao, ContactosSite
)
from restau.forms import (
    ImagemLogoForm, LogosFormSet, ImagemTopoForm, TopoFormSet, IntroForm,
    IntroFormSet, IntroImagemForm, IntroImagemFormSet, FraseCimaForm,
    FraseCimaFormSet, ImagemFraseCimaForm, ImagemFraseCimaFormSet,
    FraseInspiradoraForm, FraseInspiradoraFormSet, FraseBaixoForm,
    FraseBaixoFormSet, ImagemFraseBaixoForm, ImagemFraseBaixoFormSet,
    ImagemPadraoForm, ImagemPadraoFormSet, ContactosSiteForm,
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

            return redirect('restau:imagem_logo')
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

            return redirect('restau:imagem_topo')
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

            return redirect('restau:intro')
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

        texto_id = request.POST.get('texto_id', None)
        print('texto_id: ', texto_id)

        if texto_id:
            Intro.objects.update(is_visible=False)
            Intro.objects.filter(id=texto_id).update(is_visible=True)

            messages.success(
                request, 'Introdução escolhida com sucesso!')
            return redirect('restau:intro')

    textos = Intro.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_intro
        'textos': textos,
    }

    return render(
        request,
        'restau/pages/escolher_intro.html',
        context,
    )


def criar_intro_imagem(request):
    form_action = reverse('restau:criar_intro_imagem')
    if request.method == 'POST':
        form = IntroImagemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'imagem adicionada com sucesso!'
            )

            return redirect('restau:intro_imagem')
    else:
        form = IntroImagemForm()

    context = {
        'form_action': form_action,  # 'restau:criar_intro_imagem
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_intro_imagem.html',
        context,
    )


def apagar_intro_imagem(request, ):

    form_action = reverse('restau:apagar_intro_imagem')
    if request.method == 'POST':
        formset = IntroImagemFormSet(
            request.POST,
            request.FILES,
            queryset=IntroImagem.objects.all()
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

            return redirect('restau:intro_imagem')

    else:
        formset = IntroImagemFormSet(queryset=IntroImagem.objects.all())

    context = {
        'form_action': form_action,  # 'restau:apagar_imagem_topo
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/apagar_intro_imagem.html',
        context,
    )


def escolher_intro_imagem(request,):

    form_action = reverse('restau:escolher_intro_imagem')

    if request.method == 'POST':
        print('request.POST: ', request.POST)

        imagem_id = request.POST.get('imagem_id', None)
        print('imagem_id: ', imagem_id)

        if imagem_id:
            IntroImagem.objects.update(is_visible=False)
            IntroImagem.objects.filter(id=imagem_id).update(is_visible=True)

            messages.success(
                request, 'Imagem escolhida com sucesso!')
            return redirect('restau:imagem_topo')

    imagens = IntroImagem.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_imagem_topo
        'imagens': imagens,
    }

    return render(
        request,
        'restau/pages/escolher_intro_imagem.html',
        context,
    )


def criar_frase_cima(request):
    form_action = reverse('restau:criar_frase_cima')
    if request.method == 'POST':
        form = FraseCimaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Texto adicionado com sucesso!'
            )

            return redirect('restau:frase_cima')
    else:
        form = FraseCimaForm()

    context = {
        'form_action': form_action,  # 'restau:criar_frase_cima
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_frase_cima.html',
        context,
    )


def apagar_frase_cima(request, ):

    form_action = reverse('restau:apagar_frase_cima')
    if request.method == 'POST':
        formset = FraseCimaFormSet(
            request.POST,
            request.FILES,
            queryset=FraseCima.objects.all()
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

            return redirect('restau:frase_cima')

    else:
        formset = FraseCimaFormSet(queryset=FraseCima.objects.all())

    context = {
        'form_action': form_action,  # 'restau:apagar_frase_cima
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/apagar_frase_cima.html',
        context,
    )


def escolher_frase_cima(request,):

    form_action = reverse('restau:escolher_frase_cima')

    if request.method == 'POST':
        print('request.POST: ', request.POST)

        texto_id = request.POST.get('texto_id', None)
        print('texto_id: ', texto_id)

        if texto_id:
            FraseCima.objects.update(is_visible=False)
            FraseCima.objects.filter(id=texto_id).update(is_visible=True)

            messages.success(
                request, 'Frase escolhida com sucesso!')
            return redirect('restau:frase_cima')

    textos = FraseCima.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_frase_cima
        'textos': textos,
    }

    return render(
        request,
        'restau/pages/escolher_frase_cima.html',
        context,
    )


def criar_imagem_frase_cima(request):
    form_action = reverse('restau:criar_imagem_frase_cima')
    if request.method == 'POST':
        form = ImagemFraseCimaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Texto adicionado com sucesso!'
            )

            return redirect('restau:image_frase_cima')
    else:
        form = ImagemFraseCimaForm()

    context = {
        'form_action': form_action,  # 'restau:criar_imagem_frase_cima
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_imagem_frase_cima.html',
        context,
    )


def apagar_imagem_frase_cima(request, ):

    form_action = reverse('restau:apagar_imagem_frase_cima')
    if request.method == 'POST':
        formset = ImagemFraseCimaFormSet(
            request.POST,
            request.FILES,
            queryset=ImagemFraseCima.objects.all()
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

            return redirect('restau:imagem_frase_cima')

    else:
        formset = ImagemFraseCimaFormSet(
            queryset=ImagemFraseCima.objects.all())

    context = {
        'form_action': form_action,  # 'restau:apagar_imagem_frase_cima
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/apagar_imagem_frase_cima.html',
        context,
    )


def escolher_imagem_frase_cima(request,):

    form_action = reverse('restau:escolher_imagem_frase_cima')

    if request.method == 'POST':
        print('request.POST: ', request.POST)

        imagem_id = request.POST.get('imagem_id', None)
        print('texto_id: ', imagem_id)

        if imagem_id:
            ImagemFraseCima.objects.update(is_visible=False)
            ImagemFraseCima.objects.filter(
                id=imagem_id).update(is_visible=True)

            messages.success(
                request, 'Imagem escolhida com sucesso!')
            return redirect('restau:imagem_frase_cima')

    imagens = ImagemFraseCima.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_imagem_frase_cima
        'imagens': imagens,
    }

    return render(
        request,
        'restau/pages/escolher_imagem_frase_cima.html',
        context,
    )


def criar_frase_central(request):
    form_action = reverse('restau:criar_frase_central')
    if request.method == 'POST':
        form = FraseInspiradoraForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Texto adicionado com sucesso!'
            )

            return redirect('restau:frase_central')
    else:
        form = FraseInspiradoraForm()

    context = {
        'form_action': form_action,  # 'restau:criar_frase_central
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_frase_cima.html',
        context,
    )


def apagar_frase_central(request, ):

    form_action = reverse('restau:apagar_frase_central')
    if request.method == 'POST':
        formset = FraseInspiradoraFormSet(
            request.POST,
            request.FILES,
            queryset=FraseInspiradora.objects.all()
        )

        if formset.is_valid():
            delete_flag = False
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    if 'DELETE' in form.changed_data:
                        delete_flag = True
                        messages.success(
                            request, 'Imagem apagada com sucesso!')
                    else:
                        instance.save()

            if delete_flag:
                for form in formset:
                    if 'DELETE' in form.changed_data:
                        instance = form.instance
                        instance.delete()

            return redirect('restau:frase_central')

    else:
        formset = FraseInspiradoraFormSet(
            queryset=FraseInspiradora.objects.all())

    context = {
        'form_action': form_action,  # 'restau:apagar_frase_central
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/apagar_frase_central.html',
        context,
    )


def escolher_frase_central(request,):

    form_action = reverse('restau:escolher_frase_central')

    if request.method == 'POST':
        print('request.POST: ', request.POST)

        texto_id = request.POST.get('texto_id', None)
        print('texto_id: ', texto_id)

        if texto_id:
            FraseInspiradora.objects.update(is_visible=False)
            FraseInspiradora.objects.filter(
                id=texto_id).update(is_visible=True)

            messages.success(
                request, 'Frase escolhida com sucesso!')
            return redirect('restau:frase_central')

    textos = FraseInspiradora.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_frase_central
        'textos': textos,
    }

    return render(
        request,
        'restau/pages/escolher_frase_central.html',
        context,
    )


def criar_frase_baixo(request):
    form_action = reverse('restau:criar_frase_baixo')
    if request.method == 'POST':
        form = FraseBaixoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Texto adicionado com sucesso!'
            )

            return redirect('restau:frase_baixo')
    else:
        form = FraseBaixoForm()

    context = {
        'form_action': form_action,  # 'restau:criar_frase_baixo
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_frase_baixo.html',
        context,
    )


def apagar_frase_baixo(request, ):

    form_action = reverse('restau:apagar_frase_baixo')
    if request.method == 'POST':
        formset = FraseBaixoFormSet(
            request.POST,
            request.FILES,
            queryset=FraseBaixo.objects.all()
        )

        if formset.is_valid():
            delete_flag = False
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    if 'DELETE' in form.changed_data:
                        delete_flag = True
                        messages.success(
                            request, 'Imagem apagada com sucesso!')
                    else:
                        instance.save()

            if delete_flag:
                for form in formset:
                    if 'DELETE' in form.changed_data:
                        instance = form.instance
                        instance.delete()

            return redirect('restau:frase_baixo')

    else:
        formset = FraseBaixoFormSet(
            queryset=FraseBaixo.objects.all())

    context = {
        'form_action': form_action,  # 'restau:apagar_frase_baixo
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/apagar_frase_baixo.html',
        context,
    )


def escolher_frase_baixo(request,):

    form_action = reverse('restau:escolher_frase_baixo')

    if request.method == 'POST':
        print('request.POST: ', request.POST)

        texto_id = request.POST.get('texto_id', None)
        print('texto_id: ', texto_id)

        if texto_id:
            FraseBaixo.objects.update(is_visible=False)
            FraseBaixo.objects.filter(
                id=texto_id).update(is_visible=True)

            messages.success(
                request, 'Frase escolhida com sucesso!')
            return redirect('restau:frase_baixo')

    textos = FraseBaixo.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_frase_baixo
        'textos': textos,
    }

    return render(
        request,
        'restau/pages/escolher_frase_baixo.html',
        context,
    )


def criar_imagem_frase_baixo(request):
    form_action = reverse('restau:criar_imagem_frase_baixo')
    if request.method == 'POST':
        form = ImagemFraseBaixoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Texto adicionado com sucesso!'
            )

            return redirect('restau:image_frase_baixo')
    else:
        form = ImagemFraseBaixoForm()

    context = {
        'form_action': form_action,  # 'restau:criar_imagem_frase_baixo
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_imagem_frase_baixo.html',
        context,
    )


def apagar_imagem_frase_baixo(request, ):

    form_action = reverse('restau:apagar_imagem_frase_baixo')
    if request.method == 'POST':
        formset = ImagemFraseBaixoFormSet(
            request.POST,
            request.FILES,
            queryset=ImagemFraseBaixo.objects.all()
        )

        if formset.is_valid():
            delete_flag = False
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    if 'DELETE' in form.changed_data:
                        delete_flag = True
                        messages.success(
                            request, 'Imagem apagada com sucesso!')
                    else:
                        instance.save()

            if delete_flag:
                for form in formset:
                    if 'DELETE' in form.changed_data:
                        instance = form.instance
                        instance.delete()

            return redirect('restau:imagem_frase_baixo')

    else:
        formset = ImagemFraseBaixoFormSet(
            queryset=ImagemFraseBaixo.objects.all())

    context = {
        'form_action': form_action,  # 'restau:apagar_imagem_frase_baixo
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/apagar_imagem_frase_baixo.html',
        context,
    )


def escolher_imagem_frase_baixo(request,):

    form_action = reverse('restau:escolher_imagem_frase_baixo')

    if request.method == 'POST':
        print('request.POST: ', request.POST)

        imagem_id = request.POST.get('imagem_id', None)
        print('texto_id: ', imagem_id)

        if imagem_id:
            ImagemFraseBaixo.objects.update(is_visible=False)
            ImagemFraseBaixo.objects.filter(
                id=imagem_id).update(is_visible=True)

            messages.success(
                request, 'Imagem escolhida com sucesso!')
            return redirect('restau:imagem_frase_baixo')

    imagens = ImagemFraseBaixo.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_imagem_frase_baixo
        'imagens': imagens,
    }

    return render(
        request,
        'restau/pages/escolher_imagem_frase_baixo.html',
        context,
    )


def criar_imagem_padrao(request):
    form_action = reverse('restau:criar_imagem_padrao')
    if request.method == 'POST':
        form = ImagemPadraoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Texto adicionado com sucesso!'
            )

            return redirect('restau:image_padrao')
    else:
        form = ImagemPadraoForm()

    context = {
        'form_action': form_action,  # 'restau:criar_imagem_padrao
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_imagem_padrao.html',
        context,
    )


def apagar_imagem_padrao(request, ):

    form_action = reverse('restau:apagar_imagem_padrao')
    if request.method == 'POST':
        formset = ImagemPadraoFormSet(
            request.POST,
            request.FILES,
            queryset=ImagemPadrao.objects.all()
        )

        if formset.is_valid():
            delete_flag = False
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    if 'DELETE' in form.changed_data:
                        delete_flag = True
                        messages.success(
                            request, 'Imagem apagada com sucesso!')
                    else:
                        instance.save()

            if delete_flag:
                for form in formset:
                    if 'DELETE' in form.changed_data:
                        instance = form.instance
                        instance.delete()

            return redirect('restau:imagem_padrao')

    else:
        formset = ImagemPadraoFormSet(
            queryset=ImagemPadrao.objects.all())

    context = {
        'form_action': form_action,  # 'restau:apagar_imagem_padrao
        'formset': formset,
    }

    return render(
        request,
        'restau/pages/apagar_imagem_padrao.html',
        context,
    )


def escolher_imagem_padrao(request,):

    form_action = reverse('restau:escolher_imagem_padrao')

    if request.method == 'POST':
        print('request.POST: ', request.POST)

        imagem_id = request.POST.get('imagem_id', None)
        print('texto_id: ', imagem_id)

        if imagem_id:
            ImagemPadrao.objects.update(is_visible=False)
            ImagemPadrao.objects.filter(
                id=imagem_id).update(is_visible=True)

            messages.success(
                request, 'Imagem escolhida com sucesso!')
            return redirect('restau:imagem_padrao')

    imagens = ImagemPadrao.objects.all().order_by('id')
    context = {
        'form_action': form_action,  # 'restau:escolher_imagem_padrao
        'imagens': imagens,
    }

    return render(
        request,
        'restau/pages/escolher_imagem_padrao.html',
        context,
    )


def criar_contatos_site(request):
    contatos = ContactosSite.objects.all().first()
    print('contatos: ', contatos)
    form_action = reverse('restau:criar_contatos_site')
    if request.method == 'POST':
        form = ContactosSiteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Contato adicionado com sucesso!'
            )

            return redirect('restau:contatos_site')
    else:
        form = ContactosSiteForm()

    context = {
        'contatos': contatos,
        'form_action': form_action,  # 'restau:criar_contatos_site
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_contatos_site.html',
        context,
    )


def editar_contatos_site(request, contato_id):
    form_action = reverse('restau:editar_contatos_site',
                          kwargs={'contato_id': contato_id})
    contato = get_object_or_404(ContactosSite, id=contato_id)
    contatos = ContactosSite.objects.all().first()
    if request.method == 'POST':
        form = ContactosSiteForm(request.POST, request.FILES, instance=contato)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Contato editado com sucesso!'
            )

            return redirect('restau:contatos_site')
    else:
        form = ContactosSiteForm(instance=contato)

    context = {
        'contatos': contatos,
        'form_action': form_action,  # 'restau:criar_contatos_site
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_contatos_site.html',
        context,
    )
