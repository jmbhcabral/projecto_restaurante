from django.shortcuts import render, get_object_or_404
from restau.models import (
    Products, Category, SubCategory, ActiveSetup,)
from django.db.models import Prefetch
from collections import defaultdict


def encomendas(request):
    active_setup = ActiveSetup.objects.first()
    if active_setup:
        if active_setup.active_imagem_padrao:
            image = active_setup.active_imagem_padrao.imagem.url
            print('imagem url: ', image)
        else:
            image = 'Não tem imagem padrao'
            print('imagem url: ', image)

    if not active_setup or not active_setup.active_ementa:
        return render(request, 'restau/pages/encomendas.html', {'active_setup': active_setup, 'categorias': []})

    campo_preco = active_setup.active_ementa.nome_campo_preco_selecionado
    produtos_ementa = active_setup.active_ementa.produtos.filter(visibilidade=True).select_related(
        'categoria', 'subcategoria').order_by('categoria', 'subcategoria', 'ordem')

    categorias_dict = {}
    for produto in produtos_ementa:
        preco_dinamico = getattr(produto, campo_preco, 'Preço não definido')
        produto.preco_dinamico = preco_dinamico

        cat = produto.categoria
        subcat = produto.subcategoria

        if cat not in categorias_dict:
            categorias_dict[cat] = {'subcategorias': defaultdict(list)}

        categorias_dict[cat]['subcategorias'][subcat].append(produto)

    # Convertendo defaultdict para dict normal para evitar problemas no template
    for cat in categorias_dict.keys():
        categorias_dict[cat]['subcategorias'] = dict(
            categorias_dict[cat]['subcategorias'])

    context = {
        'active_setup': active_setup,
        'categorias': categorias_dict,
    }

    return render(request, 'restau/pages/encomendas.html', context)


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
