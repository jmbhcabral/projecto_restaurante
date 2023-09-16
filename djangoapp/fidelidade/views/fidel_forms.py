from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from fidelidade.models import Fidelidade
from restau.models import Products, Category, SubCategory, Ementa
from fidelidade.forms import FidelidadeForm
from django.contrib import messages


def criar_fidelidade(request):
    fidelidades = Fidelidade \
        .objects \
        .filter(nome__isnull=False)\
        .all()\
        .order_by('id')

    form_action = reverse('fidelidade:criar_fidelidade')

    if request.method == 'POST':
        form = FidelidadeForm(request.POST)

        context = {
            'fidelidades': fidelidades,
            'form': form,
            'form_action': form_action
        }

        if form.is_valid():
            form.save()
            return redirect('fidelidade:criar_fidelidade')

        return render(
            request,
            'fidelidade/pages/criar_fidelidade.html',
            context
        )
    context = {
        'action': 'Criar',
        'fidelidades': fidelidades,
        'form': FidelidadeForm(),
        'form_action': form_action
    }

    return render(
        request,
        'fidelidade/pages/criar_fidelidade.html',
        context
    )


def editar_fidelidade(request, fidelidade_id):
    fidelidade = get_object_or_404(
        Fidelidade, pk=fidelidade_id
    )

    form_action = reverse(
        'fidelidade:editar_fidelidade', args=(fidelidade_id,))

    if request.method == 'POST':
        form = FidelidadeForm(request.POST, instance=fidelidade)

        context = {
            'form': form,
            'form_action': form_action
        }

        if form.is_valid():
            form.save()
            return redirect('fidelidade:criar_fidelidade')

        return render(
            request,
            'fidelidade/pages/criar_fidelidade.html',
            context
        )
    context = {
        'action': 'Atualizar',
        'fidelidade': fidelidade,
        'form': FidelidadeForm(instance=fidelidade),
        'form_action': form_action
    }

    return render(
        request,
        'fidelidade/pages/criar_fidelidade.html',
        context
    )


def apagar_fidelidade(request, fidelidade_id):
    fidelidade_para_apagar = get_object_or_404(
        Fidelidade, pk=fidelidade_id
    )

    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        fidelidade_para_apagar.delete()
        return redirect('fidelidade:criar_fidelidade')

    return render(
        request,
        'fidelidade/pages/fidelidade_ind.html',
        {
            'action': 'Apagar',
            'fidelidade': fidelidade_para_apagar,
            'confirmation': confirmation
        }
    )


def pontos_produtos_fidelidade(request, fidelidade_id):
    fidelidade = get_object_or_404(
        Fidelidade, pk=fidelidade_id
    )

    ementa = Ementa.objects.all()
    categorias = Category.objects.all().order_by('ordem')
    subcategorias = SubCategory.objects.all().order_by('ordem')
    produtos = Products.objects.all().order_by('ordem')

    form_action = reverse(
        'fidelidade:pontos_produtos_fidelidade', args=(fidelidade_id,))

    if request.method == 'POST':
        form = FidelidadeForm(request.POST, fidelidade_id=fidelidade_id)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.fidelidade = fidelidade
            instance.save()

            return redirect('fidelidade:pontos_produtos_fidelidade', fidelidade_id=fidelidade_id)')

        context = {
            'fidelidade': fidelidade,
            'ementa': ementa,
            'categorias': categorias,
            'subcategorias': subcategorias,
            'produtos': produtos,
            'form': form,
            'form_action': form_action
        }

        return render(
            request,
            'fidelidade/pages/pontos_produtos_fidelidade.html',
            context
        )
    context = {
        'fidelidade': fidelidade,
        'ementa': ementa,
        'categorias': categorias,
        'subcategorias': subcategorias,
        'produtos': produtos,
        'form': FidelidadeForm(instance=fidelidade),
        'form_action': form_action
    }

    return render(
        request,
        'fidelidade/pages/pontos_produtos_fidelidade.html',
        context
    )
