from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from djangoapp.restau.forms import (
    ContactosSiteForm,
    FraseBaixoForm,
    FraseBaixoFormSet,
    FraseCimaForm,
    FraseCimaFormSet,
    FraseInspiradoraForm,
    FraseInspiradoraFormSet,
    GoogleMapsForm,
    HorarioForm,
    ImagemFraseBaixoForm,
    ImagemFraseBaixoFormSet,
    ImagemFraseCimaForm,
    ImagemFraseCimaFormSet,
    ImagemLogoForm,
    ImagemPadraoForm,
    ImagemPadraoFormSet,
    ImagemTopoForm,
    IntroForm,
    IntroFormSet,
    IntroImagemForm,
    IntroImagemFormSet,
    LogosFormSet,
    TopoFormSet,
)
from djangoapp.restau.models import (
    ActiveSetup,
    ContactosSite,
    FraseBaixo,
    FraseCima,
    FraseInspiradora,
    GoogleMaps,
    Horario,
    ImagemFraseBaixo,
    ImagemFraseCima,
    ImagemLogo,
    ImagemPadrao,
    ImagemTopo,
    Intro,
    IntroImagem,
)


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def escolher_logo(request,):

    form_action = reverse('restau:escolher_logo')

    if request.method == 'POST':
        imagem_id = request.POST.get('imagem_id', None)

        if imagem_id:
            try:
                ImagemLogo.objects.update(is_visible=False)
                logo = ImagemLogo.objects.get(id=imagem_id)
                logo.is_visible = True
                logo.save()

                active_setup = ActiveSetup.objects.first()

                if active_setup:
                    active_setup.active_imagem_logo = logo  # type: ignore
                    active_setup.save()

                messages.success(
                    request, 'Logo escolhido com sucesso!')
                return redirect('restau:imagem_logo')
            except ImagemLogo.DoesNotExist:
                messages.error(
                    request, 'Ocorreu um erro ao escolher o logo!')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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

            return redirect('restau:imagem_topo')

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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def escolher_imagem_topo(request,):

    form_action = reverse('restau:escolher_imagem_topo')

    if request.method == 'POST':
        imagem_id = request.POST.get('imagem_id', None)

        if imagem_id:
            try:
                ImagemTopo.objects.update(is_visible=False)
                imagem = ImagemTopo.objects.get(id=imagem_id)
                imagem.is_visible = True
                imagem.save()

                active_setup = ActiveSetup.objects.first()

                if active_setup:
                    active_setup.active_imagem_topo = imagem  # type: ignore
                    active_setup.save()

                messages.success(
                    request, 'Imagem escolhida com sucesso!')
                return redirect('restau:imagem_topo')
            except ImagemTopo.DoesNotExist:
                messages.error(
                    request, 'Ocorreu um erro ao escolher a imagem!')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def apagar_intro(request, ):

    form_action = reverse('restau:apagar_intro')
    if request.method == 'POST':
        formset = IntroFormSet(
            request.POST,
            request.FILES,
            queryset=Intro.objects.all()
        )

        delete_flag = False
        for form in formset:
            if 'DELETE' in form.changed_data:
                instance = form.instance
                instance.delete()
                delete_flag = True

        if delete_flag:
            messages.success(
                request, 'Introdução apagada com sucesso!')

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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def escolher_intro(request,):

    form_action = reverse('restau:escolher_intro')

    if request.method == 'POST':
        texto_id = request.POST.get('texto_id', None)

        if texto_id:
            try:
                Intro.objects.update(is_visible=False)
                texto = Intro.objects.get(id=texto_id)
                texto.is_visible = True
                texto.save()

                active_setup = ActiveSetup.objects.first()

                if active_setup:
                    active_setup.active_intro = (  # type: ignore
                        texto
                    )
                    active_setup.save()

                messages.success(
                    request, 'Introdução escolhida com sucesso!')
                return redirect('restau:intro')
            except Intro.DoesNotExist:
                messages.error(
                    request, 'Ocorreu um erro ao escolher a Introdução!')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def escolher_intro_imagem(request,):

    form_action = reverse('restau:escolher_intro_imagem')

    if request.method == 'POST':
        imagem_id = request.POST.get('imagem_id', None)

        if imagem_id:
            try:
                IntroImagem.objects.update(is_visible=False)
                imagem = IntroImagem.objects.get(id=imagem_id)
                imagem.is_visible = True
                imagem.save()

                active_setup = ActiveSetup.objects.first()

                if active_setup:
                    active_setup.active_intro_imagem = imagem  # type: ignore
                    active_setup.save()

                messages.success(
                    request, 'Imagem escolhida com sucesso!')
                return redirect('restau:intro_imagem')
            except IntroImagem.DoesNotExist:
                messages.error(
                    request, 'Ocorreu um erro ao escolher a imagem!')
                return redirect('restau:intro_imagem')

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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def apagar_frase_cima(request, ):

    form_action = reverse('restau:apagar_frase_cima')
    if request.method == 'POST':
        formset = FraseCimaFormSet(
            request.POST,
            request.FILES,
            queryset=FraseCima.objects.all()
        )

        delete_flag = False
        for form in formset:
            if 'DELETE' in form.changed_data:
                instance = form.instance
                instance.delete()
                delete_flag = True

        if delete_flag:
            messages.success(
                request, 'Frase apagada com sucesso!')

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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def escolher_frase_cima(request,):

    form_action = reverse('restau:escolher_frase_cima')

    if request.method == 'POST':
        texto_id = request.POST.get('texto_id', None)

        if texto_id:
            try:
                FraseCima.objects.update(is_visible=False)
                texto = FraseCima.objects.get(id=texto_id)
                texto.is_visible = True
                texto.save()

                active_setup = ActiveSetup.objects.first()

                if active_setup:
                    active_setup.active_frase_cima = (  # type: ignore
                        texto
                    )
                    active_setup.save()

                messages.success(
                    request, 'Frase escolhida com sucesso!')
                return redirect('restau:frase_cima')
            except FraseCima.DoesNotExist:
                messages.error(
                    request, 'Ocorreu um erro ao escolher a Frase!')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def criar_imagem_frase_cima(request):
    form_action = reverse('restau:criar_imagem_frase_cima')
    if request.method == 'POST':
        form = ImagemFraseCimaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Texto adicionado com sucesso!'
            )

            return redirect('restau:imagem_frase_cima')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def escolher_imagem_frase_cima(request,):

    form_action = reverse('restau:escolher_imagem_frase_cima')

    if request.method == 'POST':
        imagem_id = request.POST.get('imagem_id', None)

        if imagem_id:
            try:
                ImagemFraseCima.objects.update(is_visible=False)
                imagem = ImagemFraseCima.objects.get(id=imagem_id)
                imagem.is_visible = True
                imagem.save()

                active_setup = ActiveSetup.objects.first()

                if active_setup:
                    active_setup.active_imagem_frase_cima = (  # type: ignore
                        imagem
                    )
                    active_setup.save()

                messages.success(
                    request, 'Imagem escolhida com sucesso!')
                return redirect('restau:imagem_frase_cima')
            except ImagemFraseCima.DoesNotExist:
                messages.error(
                    request, 'Ocorreu um erro ao escolher a imagem!')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def apagar_frase_central(request, ):

    form_action = reverse('restau:apagar_frase_central')
    if request.method == 'POST':
        formset = FraseInspiradoraFormSet(
            request.POST,
            request.FILES,
            queryset=FraseInspiradora.objects.all()
        )

        delete_flag = False
        for form in formset:
            if 'DELETE' in form.changed_data:
                instance = form.instance
                instance.delete()
                delete_flag = True

        if delete_flag:
            messages.success(
                request, 'Frase apagada com sucesso!')

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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def escolher_frase_central(request,):

    form_action = reverse('restau:escolher_frase_central')

    if request.method == 'POST':
        texto_id = request.POST.get('texto_id', None)

        if texto_id:
            try:
                FraseInspiradora.objects.update(is_visible=False)
                texto = FraseInspiradora.objects.get(id=texto_id)
                texto.is_visible = True
                texto.save()

                active_setup = ActiveSetup.objects.first()

                if active_setup:
                    active_setup.active_frase_inspiradora = (  # type: ignore
                        texto
                    )
                    active_setup.save()

                messages.success(
                    request, 'Frase escolhida com sucesso!')
                return redirect('restau:frase_central')
            except FraseInspiradora.DoesNotExist:
                messages.error(
                    request, 'Ocorreu um erro ao escolher a Frase!')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def apagar_frase_baixo(request, ):

    form_action = reverse('restau:apagar_frase_baixo')
    if request.method == 'POST':
        formset = FraseBaixoFormSet(
            request.POST,
            request.FILES,
            queryset=FraseBaixo.objects.all()
        )

        delete_flag = False
        for form in formset:
            if 'DELETE' in form.changed_data:
                instance = form.instance
                instance.delete()
                delete_flag = True

        if delete_flag:
            messages.success(
                request, 'Frase apagada com sucesso!')

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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def escolher_frase_baixo(request,):

    form_action = reverse('restau:escolher_frase_baixo')

    if request.method == 'POST':
        texto_id = request.POST.get('texto_id', None)

        if texto_id:
            try:
                FraseBaixo.objects.update(is_visible=False)
                texto = FraseBaixo.objects.get(id=texto_id)
                texto.is_visible = True
                texto.save()

                active_setup = ActiveSetup.objects.first()

                if active_setup:
                    active_setup.active_frase_baixo = (  # type: ignore
                        texto
                    )
                    active_setup.save()

                messages.success(
                    request, 'Frase escolhida com sucesso!')
                return redirect('restau:frase_baixo')
            except FraseBaixo.DoesNotExist:
                messages.error(
                    request, 'Ocorreu um erro ao escolher a Frase!')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def criar_imagem_frase_baixo(request):
    form_action = reverse('restau:criar_imagem_frase_baixo')
    if request.method == 'POST':
        form = ImagemFraseBaixoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Texto adicionado com sucesso!'
            )

            return redirect('restau:imagem_frase_baixo')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def escolher_imagem_frase_baixo(request,):

    form_action = reverse('restau:escolher_imagem_frase_baixo')

    if request.method == 'POST':
        imagem_id = request.POST.get('imagem_id', None)

        if imagem_id:
            try:
                ImagemFraseBaixo.objects.update(is_visible=False)
                imagem = ImagemFraseBaixo.objects.get(id=imagem_id)
                imagem.is_visible = True
                imagem.save()

                active_setup = ActiveSetup.objects.first()

                if active_setup:
                    active_setup.active_imagem_frase_baixo = (  # type: ignore
                        imagem
                    )
                    active_setup.save()

                messages.success(
                    request, 'Imagem escolhida com sucesso!')
                return redirect('restau:imagem_frase_baixo')
            except ImagemFraseBaixo.DoesNotExist:
                messages.error(
                    request, 'Ocorreu um erro ao escolher a imagem!')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def criar_imagem_padrao(request):
    form_action = reverse('restau:criar_imagem_padrao')
    if request.method == 'POST':
        form = ImagemPadraoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Imagem padrão adicionada com sucesso!'
            )

            return redirect('restau:imagem_padrao')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def escolher_imagem_padrao(request,):

    form_action = reverse('restau:escolher_imagem_padrao')

    if request.method == 'POST':
        imagem_id = request.POST.get('imagem_id', None)

        if imagem_id:
            try:
                ImagemPadrao.objects.update(is_visible=False)
                imagem = ImagemPadrao.objects.get(id=imagem_id)
                imagem.is_visible = True
                imagem.save()

                active_setup = ActiveSetup.objects.first()

                if active_setup:
                    active_setup.active_imagem_padrao = (  # type: ignore
                        imagem
                    )
                    active_setup.save()

                messages.success(
                    request, 'Imagem escolhida com sucesso!')
                return redirect('restau:imagem_padrao')
            except ImagemPadrao.DoesNotExist:
                messages.error(
                    request, 'Ocorreu um erro ao escolher a imagem!')
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def criar_contatos_site(request):
    contatos = ContactosSite.objects.all().first()
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def editar_contatos_site(request, contato_id):
    form_action = reverse('restau:editar_contatos_site',
                          kwargs={'contato_id': contato_id})
    contato = get_object_or_404(ContactosSite, id=contato_id)
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
        'contato': contato,
        'form_action': form_action,  # 'restau:criar_contatos_site
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_contatos_site.html',
        context,
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def criar_google_maps(request):
    local = GoogleMaps.objects.all().first()
    form_action = reverse('restau:criar_google_maps')
    if request.method == 'POST':
        form = GoogleMapsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Local adicionado com sucesso!'
            )

            return redirect('restau:google_maps')
    else:
        form = GoogleMapsForm()

    context = {
        'local': local,
        'form_action': form_action,  # 'restau:criar_google_maps
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_google_maps.html',
        context,
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def editar_google_maps(request, map_id):
    form_action = reverse('restau:editar_google_maps',
                          kwargs={'map_id': map_id})
    local = get_object_or_404(GoogleMaps, id=map_id)
    if request.method == 'POST':
        form = GoogleMapsForm(request.POST, request.FILES, instance=local)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Local editado com sucesso!'
            )

            return redirect('restau:google_maps')
    else:
        form = GoogleMapsForm(instance=local)

    context = {
        'local': local,
        'form_action': form_action,  # 'restau:criar_google_maps
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_google_maps.html',
        context,
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def criar_horario(request):
    horario = Horario.objects.all().first()
    form_action = reverse('restau:criar_horario')
    if request.method == 'POST':
        form = HorarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Horário adicionado com sucesso!'
            )

            return redirect('restau:horario')
    else:
        form = HorarioForm()

    context = {
        'horario': horario,
        'form_action': form_action,  # 'restau:criar_horario
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_horario.html',
        context,
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def editar_horario(request, horario_id):
    form_action = reverse('restau:editar_horario',
                          kwargs={'horario_id': horario_id})
    horario = get_object_or_404(Horario, id=horario_id)

    if request.method == 'POST':
        form = HorarioForm(request.POST, request.FILES, instance=horario)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Horário editado com sucesso!'
            )

            return redirect('restau:horario')
    else:
        form = HorarioForm(instance=horario)

    context = {
        'horario': horario,
        'form_action': form_action,  # 'restau:criar_horario
        'form': form,
    }

    return render(
        request,
        'restau/pages/criar_horario.html',
        context,
    )
