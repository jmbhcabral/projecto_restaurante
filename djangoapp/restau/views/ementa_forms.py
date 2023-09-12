from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import EmentaForm
from restau.models import Ementa
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
