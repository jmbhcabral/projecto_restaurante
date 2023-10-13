from django.shortcuts import render, get_object_or_404
from restau.models import Ementa, Category, SubCategory
from django.contrib.auth.decorators import login_required, user_passes_test
from itertools import zip_longest


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def ementas(request):

    def grouper(iterable, n, fillvalue=None):
        # "Coleta dados em grupos fixos"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    ementas = Ementa.objects.all().order_by('id')
    ementas_grouped = list(grouper(ementas, 5))
    context = {
        'ementas': ementas,
        'ementas_grouped': ementas_grouped,
    }

    return render(
        request,
        'restau/pages/ementas.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def ementa(request, ementa_id):
    ementa = get_object_or_404(
        Ementa.objects.filter(pk=ementa_id,)
    )
    ementa_produtos = ementa.produtos \
        .all() \
        .order_by('ordem')

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
