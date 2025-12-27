from itertools import zip_longest

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render

from djangoapp.restau.models import SubCategory


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def Subcategorias(request):

    def grouper(iterable, n, fillvalue=None):
        # "Coleta dados em grupos fixos"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    subcategorias = SubCategory.objects.all().order_by('ordem')
    subcategorias_grouped = list(grouper(subcategorias, 5))

    context = {
        'subcategorias_grouped': subcategorias_grouped,
        'subcategorias': subcategorias,
    }
    return render(
        request,
        'restau/pages/subcategorias.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def subcategoria(request, subcategoria_id):
    subcategoria = get_object_or_404(
        SubCategory.objects
        .filter(pk=subcategoria_id,))

    context = {
        'subcategoria': subcategoria,
    }

    return render(
        request,
        'restau/pages/subcategoria.html',
        context,

    )
