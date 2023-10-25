from django.shortcuts import render, get_object_or_404
from restau.models import (
    Products, Category, SubCategory, ActiveSetup,)
from django.db.models import Prefetch


def encomendas(request):
    active_setup = ActiveSetup.objects.first()

    categorias = Category.objects \
        .all() \
        .order_by('ordem')
    subcategorias = SubCategory.objects \
        .all() \
        .order_by('ordem')

    ementa = active_setup.active_ementa
    campo_preco = ementa.nome_campo_preco_selecionado

    if active_setup and active_setup.active_ementa:
        produtos_ementa = active_setup.active_ementa.produtos \
            .all() \
            .order_by('categoria', 'subcategoria', 'ordem')

        produtos_ementa = produtos_ementa.prefetch_related(
            Prefetch('categoria', queryset=categorias),
            Prefetch('subcategoria', queryset=subcategorias)
        )

        for produto in produtos_ementa:
            preco = getattr(produto, campo_preco, None)
            if preco is not None:
                produto.preco_dinamico = preco
            else:
                produto.preco_dinamico = 'Preço não definido'

    else:
        produtos_ementa = Products.objects.none()

    context = {
        'active_setup': active_setup,
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
