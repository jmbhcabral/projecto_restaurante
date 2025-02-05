from django.shortcuts import render, get_object_or_404
from restau.models import (
    Products, Category, SubCategory, ActiveSetup, ProdutosEmenta
    )
from django.db.models import Prefetch
from collections import defaultdict
from django.contrib.auth.decorators import login_required, user_passes_test


def encomendas(request):
    active_setup = ActiveSetup.objects.first()

    if not active_setup or not active_setup.active_ementa:
        return render(request, 'restau/pages/encomendas.html', {'active_setup': active_setup, 'categorias': {}})

    # Definir o campo de preço escolhido na ementa
    campo_preco = active_setup.active_ementa.nome_campo_preco_selecionado

    # Buscar produtos da ementa com suas descrições personalizadas e categorias associadas
    produtos_ementa = ProdutosEmenta.objects.filter(
        ementa=active_setup.active_ementa,
        produto__visibilidade=True
    ).select_related('produto', 'produto__categoria', 'produto__subcategoria').order_by('produto__ordem')

    # Dicionário para armazenar categorias e subcategorias ordenadas
    categorias_dict = defaultdict(lambda: {'subcategorias': defaultdict(list)})

    # Criar categorias e subcategorias ordenadas
    categorias = Category.objects.all().order_by('ordem')
    subcategorias = SubCategory.objects.all().order_by('ordem')

    for pe in produtos_ementa:
        if pe.produto:
            produto = pe.produto
            produto.preco_dinamico = getattr(produto, campo_preco, 'Preço não definido')
            produto.descricao_final = pe.descricao if pe.descricao else produto.descricao_curta  # Definir descrição final

            cat = produto.categoria
            subcat = produto.subcategoria

            categorias_dict[cat]['subcategorias'][subcat].append(produto)

    # Ordenar os produtos dentro das categorias e subcategorias
    for cat, cat_data in categorias_dict.items():
        # Criar um novo defaultdict para as subcategorias ordenadas
        subcategorias_ordenadas = defaultdict(list)
        # Primeiro, ordenar as subcategorias pela ordem
        sorted_subcats = sorted(cat_data['subcategorias'].items(), key=lambda x: x[0].ordem if x[0] else 0)
        for subcat, produtos in sorted_subcats:
            subcategorias_ordenadas[subcat] = sorted(produtos, key=lambda p: p.ordem)
        cat_data['subcategorias'] = dict(subcategorias_ordenadas)  # Converter para dict regular

    context = {
        'active_setup': active_setup,
        'categorias': dict(sorted(categorias_dict.items(), key=lambda c: c[0].ordem)),  # Ordenar categorias
        'todas_categorias': categorias,  # Adicionando ao contexto
        'todas_subcategorias': subcategorias,  # Adicionando ao contexto
    }

    return render(request, 'restau/pages/encomendas.html', context)


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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
