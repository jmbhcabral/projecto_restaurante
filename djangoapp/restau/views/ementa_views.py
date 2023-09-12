from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import EmentaForm
from restau.models import Ementa
from django.contrib.auth.decorators import login_required, user_passes_test


def ementa(request, ementa_id):
    ementa = get_object_or_404(
        Ementa.objects.filter(pk=ementa_id,)
    )

    context = {
        'ementa': ementa,
    }

    return render(
        request,
        'restau/pages/ementa.html',
        context
    )
