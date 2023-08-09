from django.shortcuts import render, get_object_or_404
from restau.models import Products, FrontendSetup


PER_PAGE = 9


def index(request):
    main_logo = FrontendSetup.objects \
        .filter(imagem_logo__isnull=False) \
        .order_by('-id') \
        .first()

    main_image = FrontendSetup.objects \
        .filter(imagem_topo__isnull=False) \
        .order_by('-id') \
        .first()
    return render(
        request,
        'restau/pages/index.html',
        {'main_logo': main_logo,
         'main_image': main_image},
    )


def admin_home(request):
    produtos = Products.objects \
        .order_by('id')

    return render(
        request,
        'restau/pages/admin-home.html',
        {'produtos': produtos},

    )


def product(request, product_id):
    single_product = get_object_or_404(
        Products.objects
        .filter(pk=product_id,))

    context = {
        'product': single_product,
    }

    return render(
        request,
        'restau/pages/produto.html',
        context,

    )
