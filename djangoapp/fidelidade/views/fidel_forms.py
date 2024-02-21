from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.forms import formset_factory
from fidelidade.models import Fidelidade, ProdutoFidelidadeIndividual
from restau.models import Category, SubCategory
from utils.model_validators import calcular_pontos
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
    preco_field = ementa.nome_campo_preco_selecionado

    if preco_field is None:
        messages.error(
            request,
            f'A ementa { ementa } não tem um'
            f' preço definido no campo {preco_field}'
        )
        return redirect(
            'fidelidade:fidelidade')

    categorias = (Category
                  .objects
                  .all()
                  .order_by('ordem'))
    subcategorias = SubCategory.objects.all().order_by('ordem')
    produtos = (ementa.produtos
                .select_related('categoria', 'subcategoria')
                .all()
                .order_by('ordem'))

    form_action = reverse(
        'fidelidade:pontos_produtos_fidelidade', args=(fidelidade_id,))

    ProdutoFidelidadeIndividualFormSet = formset_factory(
        ProdutoFidelidadeIndividualForm, extra=0)
    initial_data = []
    for produto in produtos:
        produto_fidelidade = ProdutoFidelidadeIndividual.objects.filter(
            produto=produto, fidelidade=fidelidade).first()

        preco = getattr(produto, preco_field, None)
        if preco is None:

            messages.error(
                request,
                f'O produto { produto } não tem um'
                f' preço definido no campo {preco_field}'
            )

            return redirect(
                'fidelidade:fidelidade', fidelidade_id)

        if produto_fidelidade:
            subcategoria_nome = produto.subcategoria.nome if \
                produto.subcategoria else "Sem Subcategoria"
            initial_data.append({
                'produto_nome': produto.nome,
                'categoria': produto.categoria.nome,
                'subcategoria': subcategoria_nome,
                'fidelidade': produto_fidelidade.fidelidade.pk,
                'produto': produto_fidelidade.produto.pk,
                'pontos_recompensa': produto_fidelidade.pontos_recompensa,
                'pontos_para_oferta': produto_fidelidade.pontos_para_oferta,
                'visibilidade': produto_fidelidade.visibilidade,
            })
        else:

            pontos_recompensa, pontos_para_oferta = calcular_pontos(
                produto, fidelidade)
            initial_data.append({
                'produto_nome': produto.nome,
                'categoria': produto.categoria.nome,
                'subcategoria': produto.subcategoria.nome if produto
                .subcategoria else "Sem Subcategoria",
                'fidelidade': fidelidade.pk,
                'produto': produto.pk,
                'pontos_recompensa': pontos_recompensa,
                'pontos_para_oferta': pontos_para_oferta,
                'visibilidade': False,
            })
    print('initial data: ', initial_data)

    print('aqui-get')

    if request.method == 'POST':
        print('request is post:', request.POST)
        formset = ProdutoFidelidadeIndividualFormSet(
            request.POST,)
        print('aqui-post')
        print('post formset: ', formset)

        if formset.is_valid():
            for form in formset:

                produto_atual = form.cleaned_data['produto']
                if produto_atual:
                    print('produto atual: ', produto_atual.nome)

                if form.has_changed():
                    print('form changed')
                    produto = form.cleaned_data['produto']
                    print('produto:', produto)
                    fidelidade = form.cleaned_data['fidelidade']
                    pontos_recompensa = form.cleaned_data['pontos_recompensa']
                    pontos_para_oferta = (
                        form.cleaned_data['pontos_para_oferta'])
                    visibilidade = form.cleaned_data['visibilidade']

                    ProdutoFidelidadeIndividual.objects.update_or_create(
                        produto=produto,
                        fidelidade=fidelidade,
                        defaults={
                            'pontos_recompensa': pontos_recompensa,
                            'pontos_para_oferta': pontos_para_oferta,
                            'visibilidade': visibilidade
                        }
                    )
                else:
                    print('form not changed')
                    messages.info(
                        request,
                        'Nenhum ponto foi atualizado.'
                    )

            messages.success(request, 'Pontos atualizados com sucesso.')
            return redirect(
                'fidelidade:pontos_produtos_fidelidade', fidelidade_id)

        else:
            print('formset: ', formset)
            print('AQUI')
            print('formset is not valid')
            for e in formset.errors:
                print('ERRO:', e)

            messages.error(request, 'Erro ao atualizar pontos.')

            return render(
                request,
                'fidelidade/pages/pontos_produtos_fidelidade.html',
                {
                    'fidelidade': fidelidade,
                    'categorias': categorias,
                    'subcategorias': subcategorias,
                    'ementa': ementa,
                    # 'produto': produto,
                    'produtos': produtos,
                    'formset': formset,
                    'form_action': form_action,
                }
            )

    else:
        formset = ProdutoFidelidadeIndividualFormSet(
            initial=initial_data,
        )

        context = {
            'fidelidade': fidelidade,
            'categorias': categorias,
            'subcategorias': subcategorias,
            'ementa': ementa,
            'produtos': produtos,
            # 'produto': produto,
            'formset': formset,
            'form_action': form_action,
        }

        return render(
            request,
            'fidelidade/pages/pontos_produtos_fidelidade.html',
            context
        )
