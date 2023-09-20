from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.forms import formset_factory
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
    print('fidelidade_id:', fidelidade_id)
    print('Fidelidade_capturada: ', fidelidade)

    ementa = fidelidade.ementa
    categorias = Category.objects.all().order_by('ordem')
    subcategorias = SubCategory.objects.all().order_by('ordem')
    produtos = ementa.produtos.all().order_by('ordem')

    form_action = reverse(
        'fidelidade:pontos_produtos_fidelidade', args=(fidelidade_id,))

    ProdutoFidelidadeIndividualFormSet = formset_factory(
        ProdutoFidelidadeIndividualForm, extra=0)

    initial_data = []
    for produto in produtos:
        try:
            produto_fidelidade = ProdutoFidelidadeIndividual.objects.get(
                produto=produto, fidelidade=fidelidade)
            initial_data.append({
                'produto_nome': produto.nome,
                'fidelidade': produto_fidelidade.fidelidade.pk,
                'produto': produto_fidelidade.produto.pk,
                'pontos_recompensa': produto_fidelidade.pontos_recompensa,
                'pontos_para_oferta': produto_fidelidade.pontos_para_oferta
            })
        except ProdutoFidelidadeIndividual.DoesNotExist:
            initial_data.append({
                'produto_nome': produto.nome,
                'fidelidade': fidelidade,
                # 'produto': produto_fidelidade.produto.pk,
                'pontos_recompensa': 0,
                'pontos_para_oferta': 0
            })

    print('INITIAL_DATA: ', initial_data)

    if request.method == 'POST':
        print('request is post:', request.POST)
        formset = ProdutoFidelidadeIndividualFormSet(
            request.POST, )

        if formset.is_valid():
            print('formset is valid')
            for form in formset:
                print(form.cleaned_data)
                if form.has_changed():

                    print('Fidelidade:', fidelidade)
                    print('Fidelidade_id:', fidelidade_id)
                    instance = form.save(commit=False)
                    print('instance to save:', instance)
                    instance.fidelidade = fidelidade
                    instance.save()
                    print('instance saved:', instance)

                else:
                    print('form not changed')

            messages.success(request, 'Pontos atualizados com sucesso.')
            return redirect(
                'fidelidade:pontos_produtos_fidelidade', fidelidade_id)

        else:
            print('formset is not valid')
            for e in formset.errors:
                print('ERRO:', e)

            messages.error(request, 'Erro ao atualizar pontos.')

            return render(
                request,
                'fidelidade/pages/pontos_produtos_fidelidade.html',
                {
                    'fidelidade': fidelidade,
                    'ementa': ementa,
                    'categorias': categorias,
                    'subcategorias': subcategorias,
                    'produtos': produtos,
                    'formset': formset,
                    'form_action': form_action,
                }
            )

    else:
        formset = ProdutoFidelidadeIndividualFormSet(
            initial=initial_data,
            # form_kwargs={'ementa': ementa, }
        )

        context = {
            'fidelidade': fidelidade,
            'ementa': ementa,
            'categorias': categorias,
            'subcategorias': subcategorias,
            'produtos': produtos,
            'formset': formset,
            'form_action': form_action,
        }

        return render(
            request,
            'fidelidade/pages/pontos_produtos_fidelidade.html',
            context
        )
