from django.shortcuts import render, get_object_or_404
from restau.models import Products


PER_PAGE = 9


def index(request):
    return render(
        request,
        'restau/pages/index.html'
    )


def admin_home(request):
    produtos = Products.objects \
        .filter(visibilidade=True) \
        .order_by('id')

    return render(
        request,
        'restau/pages/admin-home.html',
        {'produtos': produtos},

    )


def product(request, product_id):
    single_product = get_object_or_404(
        Products.objects
        .filter(pk=product_id, visibilidade=True))

    context = {
        'product': single_product,
    }

    return render(
        request,
        'restau/pages/produto.html',
        context,

    )
