from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from fidelidade.models import Fidelidade, ProdutoFidelidadeIndividual
from restau.models import Category, SubCategory
from fidelidade.forms import FidelidadeForm, ProdutoFidelidadeIndividualForm
from django.contrib import messages


def criar_fidelidade(request):
    fidelidades = Fidelidade \
        .objects \
        .filter(nome__isnull=False)\
        .all()\
        .order_by('id')

    form_action = reverse('fidelidade:criar_fidelidade')

    if request.method == 'POST':
        form = FidelidadeForm(request.POST)

        context = {
            'fidelidades': fidelidades,
            'form': form,
            'form_action': form_action
        }

        if form.is_valid():
            form.save()
            return redirect('fidelidade:criar_fidelidade')

        return render(
            request,
            'fidelidade/pages/criar_fidelidade.html',
            context
        )
    context = {
        'action': 'Criar',
        'fidelidades': fidelidades,
        'form': FidelidadeForm(),
        'form_action': form_action
    }

    return render(
        request,
        'fidelidade/pages/criar_fidelidade.html',
        context
    )


def editar_fidelidade(request, fidelidade_id):
    fidelidade = get_object_or_404(
        Fidelidade, pk=fidelidade_id
    )

    form_action = reverse(
        'fidelidade:editar_fidelidade', args=(fidelidade_id,))

    if request.method == 'POST':
        form = FidelidadeForm(request.POST, instance=fidelidade)

        context = {
            'form': form,
            'form_action': form_action
        }

        if form.is_valid():
            form.save()
            return redirect('fidelidade:criar_fidelidade')

        return render(
            request,
            'fidelidade/pages/criar_fidelidade.html',
            context
        )
    context = {
        'action': 'Atualizar',
        'fidelidade': fidelidade,
        'form': FidelidadeForm(instance=fidelidade),
        'form_action': form_action
    }

    return render(
        request,
        'fidelidade/pages/criar_fidelidade.html',
        context
    )


def apagar_fidelidade(request, fidelidade_id):
    fidelidade_para_apagar = get_object_or_404(
        Fidelidade, pk=fidelidade_id
    )

    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        fidelidade_para_apagar.delete()
        return redirect('fidelidade:criar_fidelidade')

    return render(
        request,
        'fidelidade/pages/fidelidade_ind.html',
        {
            'action': 'Apagar',
            'fidelidade': fidelidade_para_apagar,
            'confirmation': confirmation
        }
    )


def pontos_produtos_fidelidade(request, fidelidade_id):
    fidelidade = get_object_or_404(
        Fidelidade, pk=fidelidade_id
    )

    ementa = fidelidade.ementa
    categorias = Category.objects.all().order_by('ordem')
    subcategorias = SubCategory.objects.all().order_by('ordem')
    produtos = ementa.produtos.all().order_by('ordem')

    form_action = reverse(
        'fidelidade:pontos_produtos_fidelidade', args=(fidelidade_id,))

    produtos_fidelidade_map = {}
    for produto in produtos:
        try:
            produto_fidelidade = ProdutoFidelidadeIndividual.objects.get(
                produto=produto)
            produtos_fidelidade_map[produto.id] = produto_fidelidade
            print(produtos_fidelidade_map[produto.id])
        except ProdutoFidelidadeIndividual.DoesNotExist:
            produtos_fidelidade_map[produto.id] = None

    if request.method == 'POST':
        bulk_list = []
        bulk_update_list = []
        for produto in produtos:
            pontos_recompensa = request.POST.get(
                f'pontos_recompensa_{produto.id}', None)
            pontos_para_oferta = request.POST.get(
                f'pontos_para_oferta_{produto.id}', None)

            if pontos_recompensa in [None, ""]:
                pontos_recompensa = None
            if pontos_para_oferta in [None, ""]:
                pontos_para_oferta = None

            try:
                produto_fidelidade = ProdutoFidelidadeIndividual.objects.get(
                    produto=produto)
                produto.pontos_recompensa = produto_fidelidade.pontos_recompensa

                produto.pontos_para_oferta = produto_fidelidade.pontos_para_oferta

                if pontos_recompensa is not None:
                    produto_fidelidade.pontos_recompensa = pontos_recompensa

                if pontos_para_oferta is not None:
                    produto_fidelidade.pontos_para_oferta = pontos_para_oferta

                bulk_update_list.append(produto_fidelidade)
            except ProdutoFidelidadeIndividual.DoesNotExist:

                novo_objecto = ProdutoFidelidadeIndividual(
                    produto=produto,
                    pontos_recompensa=pontos_recompensa,
                    pontos_para_oferta=pontos_para_oferta,
                    fidelidade=fidelidade,
                )
                bulk_list.append(novo_objecto)

        if bulk_list:
            ProdutoFidelidadeIndividual.objects.bulk_create(bulk_list)

        if bulk_update_list:
            ProdutoFidelidadeIndividual.objects.bulk_update(
                bulk_update_list, ['pontos_recompensa', 'pontos_para_oferta'])

        return redirect('fidelidade:pontos_produtos_fidelidade',
                        fidelidade_id=fidelidade_id)

    else:
        form = ProdutoFidelidadeIndividualForm()

        context = {
            'fidelidade': fidelidade,
            'ementa': ementa,
            'categorias': categorias,
            'subcategorias': subcategorias,
            'produtos': produtos,
            'form': form,
            'form_action': form_action,
            'produtos_fidelidade_map': produtos_fidelidade_map
        }

        return render(
            request,
            'fidelidade/pages/pontos_produtos_fidelidade.html',
            context
        )
