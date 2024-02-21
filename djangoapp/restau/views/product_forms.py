from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import ProductForm
from restau.models import Products, SubCategory, Category
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def criar_produto(request):
    form_action = reverse('restau:criar_produto')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            form.save()
            return redirect('restau:criar_produto')

        return render(
            request,
            'restau/pages/criar_produto.html',
            context
        )

    context = {
        'form': ProductForm(),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/criar_produto.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def atualizar_produto(request, produto_id):
    produto = get_object_or_404(
        Products, pk=produto_id)
    form_action = reverse('restau:atualizar_produto', args=(produto_id,))
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=produto)
        context = {
            'produto': produto,
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            produto = form.save()
            return redirect('restau:produtos')

        return render(
            request,
            'restau/pages/criar_produto.html',
            context
        )

    context = {
        'produto': produto,
        'form': ProductForm(instance=produto),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/criar_produto.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def apagar_produto(request, produto_id):
    produto = get_object_or_404(
        Products, pk=produto_id, visibilidade=True
    )
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        produto.delete()
        return redirect('restau:produtos')

    return render(
        request,
        'restau/pages/produto.html',
        {
            'produto': produto,
            'confirmation': confirmation,
        }
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def ordenar_produtos(request):
    categorias = Category.objects \
        .all() \
        .order_by('ordem')

    subcategorias = SubCategory.objects \
        .all() \
        .order_by('ordem')

    Produtosformset = modelformset_factory(
        Products, fields=('nome', 'ordem'), extra=0
    )
    formset = Produtosformset(queryset=Products.objects
                              .all()
                              .order_by('ordem')
                              )
    form_action = reverse('restau:ordenar_produtos')

    if request.method == 'POST':
        formset = Produtosformset(request.POST,
                                  request.FILES,
                                  queryset=Products.objects.all(),
                                  )
        context = {
            'categorias': categorias,
            'subcategorias': subcategorias,
            'formset': formset,
            'form_action': form_action,
        }
        if formset.is_valid():
            formset.save()
            return redirect('restau:ordenar_produtos')

        else:
            print(f'formset: {formset.errors}')

        return render(
            request,
            'restau/pages/ordenar_produtos.html',
            context
        )
    context = {
        'categorias': categorias,
        'subcategorias': subcategorias,
        'formset': formset,
        'form': ProductForm(),
        'form_action': form_action,
    }

    return render(
        request,
        'restau/pages/ordenar_produtos.html',
        context
    )
