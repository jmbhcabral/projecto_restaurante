from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import EmentaForm, ProdutosEmentaForm
from restau.models import (
    Ementa, Products, ProdutosEmenta, Category,
    SubCategory
)
from django.contrib.auth.decorators import login_required, user_passes_test


def ementas_create(request):
    ementas = Ementa.objects \
        .filter(nome__isnull=False) \
        .all() \
        .order_by('id')

    form_action = reverse('restau:ementas_create')

    if request.method == 'POST':
        form = EmentaForm(request.POST, )
        context = {
            'ementas': ementas,
            'form': form,
            'form_action': form_action
        }
        if form.is_valid():
            form.save()
            return redirect('restau:ementas_create')

        return render(
            request,
            'restau/pages/ementas_create.html',
            context
        )

    context = {
        'ementas': ementas,
        'form': EmentaForm(),
        'form_action': form_action
    }

    return render(
        request,
        'restau/pages/ementas.html',
        context
    )


def ementas_update(request, ementa_id):
    ementa = get_object_or_404(
        Ementa, pk=ementa_id
    )
    form_action = reverse('restau:ementas_update', args=(ementa_id,))
    if request.method == 'POST':
        form = EmentaForm(request.POST, instance=ementa)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            ementa = form.save()
            return redirect('restau:ementas_create')

        return render(
            request,
            'restau/pages/ementas.html',
            context
        )

    context = {
        'form': EmentaForm(instance=ementa),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/ementas.html',
        context
    )


def ementas_delete(request, ementa_id):
    ementa_para_apagar = get_object_or_404(
        Ementa, pk=ementa_id,
    )
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        ementa_para_apagar.delete()
        return redirect('restau:ementas_create')

    return render(
        request,
        'restau/pages/ementa.html',
        {
            'ementa': ementa_para_apagar,
            'confirmation': confirmation,
        }
    )


def povoar_ementa(request, ementa_id):
    ementa = get_object_or_404(Ementa, pk=ementa_id)

    categorias = Category.objects.all().order_by('ordem')
    subcategorias = SubCategory.objects.all().order_by('ordem')
    artigo = Products.objects.all().order_by('ordem')

    form_action = reverse('restau:povoar_ementa', args=[ementa_id])

    if request.method == 'POST':
        form = ProdutosEmentaForm(request.POST, ementa_id=ementa_id)
        if form.is_valid():
            form.save()
            # Or wherever you'd like to redirect
            return redirect('restau:povoar_ementa', args=[ementa_id])

        context = {
            'form': form,
            'form_action': form_action,
            'ementa': ementa,
            'artigo': artigo,
            'categorias': categorias,
            'subcategorias': subcategorias,
        }
        return render(request, 'restau/pages/povoar_ementa.html', context)

    else:
        form = ProdutosEmentaForm(ementa_id=ementa_id)

    context = {
        'ementa': ementa,
        'artigo': artigo,
        'categorias': categorias,
        'subcategorias': subcategorias,
        'form': form,
        'form_action': form_action,
    }

    return render(request, 'restau/pages/povoar_ementa.html', context)
