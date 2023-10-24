from django.shortcuts import render, get_object_or_404
from restau.models import (
    Products, Category, SubCategory, ActiveSetup,)
from fidelidade.models import (
    ProdutoFidelidadeIndividual)
from django.db.models import Prefetch


def encomendas(request):
    active_setup = ActiveSetup.objects.first()

    categorias = Category.objects \
        .all() \
        .order_by('ordem')
    subcategorias = SubCategory.objects \
        .all() \
        .order_by('ordem')

    frontend_setup = ActiveSetup.objects \
        .order_by('-id') \
        .first()

    produtos_fidelidade = ProdutoFidelidadeIndividual.objects.all()

    if frontend_setup and frontend_setup.active_ementa:
        produtos_ementa = frontend_setup.active_ementa.produtos \
            .all() \
            .order_by('categoria', 'subcategoria', 'ordem')
        print('active_ementa', frontend_setup.active_ementa)
    else:
        produtos_ementa = Products.objects.none()

    produtos_ementa = produtos_ementa.prefetch_related(
        Prefetch('categoria', queryset=categorias),
        Prefetch('subcategoria', queryset=subcategorias)
    )

    for p in produtos_fidelidade:
        print('p.produto', p.produto)
        for q in produtos_ementa:
            print('q', q)
            if p.produto == q:
                print(f'{p.produto} = {q}')

    context = {
        'produtos_fidelidade': produtos_fidelidade,
        'active_setup': active_setup,
        'frontend_setup': frontend_setup,
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
