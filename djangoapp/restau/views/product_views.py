from django.shortcuts import render, get_object_or_404
from restau.models import (
    Products, FrontendSetup, Category, SubCategory, )
from django.db.models import Prefetch


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

    categorias = Category.objects \
        .all() \
        .order_by('ordem')
    subcategorias = SubCategory.objects \
        .all() \
        .order_by('ordem')

    frontend_setup = FrontendSetup.objects \
        .order_by('-id') \
        .first()

    if frontend_setup and frontend_setup.ementa:
        produtos_ementa = frontend_setup.ementa.produtos \
            .all() \
            .order_by('categoria', 'subcategoria', 'ordem')

    else:
        produtos_ementa = Products.objects.none()

    produtos_ementa = produtos_ementa.prefetch_related(
        Prefetch('categoria', queryset=categorias),
        Prefetch('subcategoria', queryset=subcategorias)
    )

    # produtos_queryset = Products.objects.all().order_by(
    #     'categoria', 'subcategoria', 'ordem')
    # produtos = produtos_queryset.prefetch_related(
    #     Prefetch('categoria', queryset=categorias),
    #     Prefetch('subcategoria', queryset=subcategorias)
    # )
    context = {
        'main_logo': main_logo,
        'main_image': main_image,
        'default_image': default_image,
        'produtos': produtos_ementa,
        'categorias': categorias,
        'subcategorias': subcategorias,
    }
    return render(
        request,
        'restau/pages/encomendas.html',
        context,
    )


def produtos(request):
    categorias = Category.objects \
        .all() \
        .order_by('ordem')
    subcategorias = SubCategory.objects \
        .all() \
        .order_by('ordem')

    produtos_queryset = Products.objects.all().order_by(
        'categoria', 'subcategoria', 'ordem')
    produtos = produtos_queryset.prefetch_related(
        Prefetch('categoria', queryset=categorias),
        Prefetch('subcategoria', queryset=subcategorias)
    )
    return render(
        request,
        'restau/pages/produtos.html', {
            'produtos': produtos,
            'categorias': categorias,
            'subcategorias': subcategorias,
        },

    )


def produto(request, produto_id):
    produto = get_object_or_404(
        Products.objects
        .filter(pk=produto_id,))

    context = {
        'produto': produto,
    }

    return render(
        request,
        'restau/pages/produto.html',
        context,

    )
