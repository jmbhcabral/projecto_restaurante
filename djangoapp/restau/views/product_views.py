from django.shortcuts import render, get_object_or_404
from restau.models import Products, FrontendSetup, Category, SubCategory


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


def encomendas(request):
    main_logo = FrontendSetup.objects \
        .filter(imagem_logo__isnull=False) \
        .order_by('-id') \
        .first()

    main_image = FrontendSetup.objects \
        .filter(imagem_topo__isnull=False) \
        .order_by('-id') \
        .first()

    default_image = FrontendSetup.objects \
        .filter(imagem_topo__isnull=False) \
        .order_by('-id') \
        .first()

    produtos = Products.objects \
        .all() \
        .order_by('id')

    categorias = Category.objects \
        .all() \
        .order_by('ordem')

    subcategorias = SubCategory.objects \
        .all() \
        .order_by('ordem')

    return render(
        request,
        'restau/pages/encomendas.html',
        {
            'main_logo': main_logo,
            'main_image': main_image,
            'default_image': default_image,
            'produtos': produtos,
            'categorias': categorias,
            'subcategorias': subcategorias,
        },
    )


def produtos(request):
    categorias = Category.objects \
        .all() \
        .order_by('ordem')
    subcategorias = SubCategory.objects \
        .all() \
        .order_by('ordem')

    produtos = Products.objects \
        .all() \
        .order_by('id')

    return render(
        request,
        'restau/pages/produtos.html', {
            'produtos': produtos,
            'categorias': categorias,
            'subcategorias': subcategorias,
        },

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
