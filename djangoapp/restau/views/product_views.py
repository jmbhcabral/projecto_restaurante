from django.shortcuts import render, get_object_or_404
from restau.models import (
    Products, Category, SubCategory, ActiveSetup, ProdutosEmenta
    )
from django.db.models import Prefetch
from collections import defaultdict
from django.contrib.auth.decorators import login_required, user_passes_test


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

    # Alteração para buscar os produtos corretamente
    produtos_ementa = ProdutosEmenta.objects.filter(
        ementa=active_setup.active_ementa)\
            .select_related('produto')\
            .filter(produto__visibilidade=True)\
            .order_by('produto__ordem')

    categorias_dict = {}
    for pe in produtos_ementa:

        if pe.produto:
            produto = pe.produto
            print('produto: ', produto)
            preco_dinamico = getattr(produto, campo_preco, 'Preço não definido')
            descricao = pe.descricao if pe.descricao else produto.descricao_curta


            produto.preco_dinamico = preco_dinamico
            produto.descricao_final = descricao  # Passar a descrição correta

        cat = produto.categoria
        subcat = produto.subcategoria

        if cat not in categorias_dict:
            categorias_dict[cat] = {'subcategorias': defaultdict(list)}

        categorias_dict[cat]['subcategorias'][subcat].append(produto)

    # Convertendo defaultdict para dict normal para evitar problemas no template
    for cat in categorias_dict.keys():
        categorias_dict[cat]['subcategorias'] = dict(categorias_dict[cat]['subcategorias'])

    context = {
        'active_setup': active_setup,
        'categorias': categorias_dict,
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
