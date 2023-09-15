from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import EmentaForm
from restau.models import Ementa, Category, SubCategory
from django.contrib.auth.decorators import login_required, user_passes_test


def ementa(request, ementa_id):
    ementa = get_object_or_404(
        Ementa.objects.filter(pk=ementa_id,)
    )
    ementa_produtos = ementa.produtos.all().order_by('ordem')

    categorias = Category.objects.all().order_by('ordem')
    subcategorias = SubCategory.objects.all().order_by('ordem')

    context = {
        'categorias': categorias,
        'subcategorias': subcategorias,
        'ementa': ementa,
        'ementa_produtos': ementa_produtos,
    }

    return render(
        request,
        'restau/pages/ementa.html',
        context
    )
