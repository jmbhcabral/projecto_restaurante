from itertools import zip_longest

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render

from djangoapp.restau.models import Category


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def categorias(request):
    def grouper(iterable, n, fillvalue=None):
        # "Coleta dados em grupos fixos"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    categorias = Category.objects.all().order_by('ordem')
    categorias_grouped = list(grouper(categorias, 5))

    context = {
        'categorias_grouped': categorias_grouped,
        'categorias': categorias,
    }

    return render(
        request,
        'restau/pages/categorias.html',
        context,
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def categoria(request, categoria_id):
    categoria = get_object_or_404(
        Category.objects
        .filter(pk=categoria_id,))

    context = {
        'categoria': categoria,
    }

    return render(
        request,
        'restau/pages/categoria.html',
        context,

    )
