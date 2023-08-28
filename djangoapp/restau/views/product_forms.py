from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import ProductForm
from restau.models import Products, SubCategory, Category
from django.forms import modelformset_factory


def create_product(request):
    form_action = reverse('restau:create_product')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            form.save()
            return redirect('restau:create_product')

        return render(
            request,
            'restau/pages/create_product.html',
            context
        )

    context = {
        'form': ProductForm(),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/create_product.html',
        context
    )


def update(request, product_id):
    product = get_object_or_404(
        Products, pk=product_id)
    form_action = reverse('restau:update', args=(product_id,))
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            product = form.save()
            return redirect('restau:produtos')

        return render(
            request,
            'restau/pages/create_product.html',
            context
        )

    context = {
        'form': ProductForm(instance=product),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/create_product.html',
        context
    )


def delete(request, product_id):
    product = get_object_or_404(
        Products, pk=product_id, visibilidade=True
    )
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        product.delete()
        return redirect('restau:produtos')

    return render(
        request,
        'restau/pages/produto.html',
        {
            'product': product,
            'confirmation': confirmation,
        }
    )


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

    print('-------------------------------------')
    print('-------------------------------------')
    print('--------------DEBUGGING--------------')
    print('-------------------------------------')
    print('-------------------------------------')

    for cat in categorias:
        print(f'categoria: {cat.nome}')
        for subcat in subcategorias:
            if subcat.categoria == cat:
                print(f'subcategoria: {subcat.nome}')
                for produto in formset:
                    # print(f'produto: {produto.instance.nome}')
                    if produto.instance.categoria == cat and \
                            produto.instance.subcategoria == subcat:
                        # print(f'categoria: {cat.nome}')
                        # print(f'subcategoria: {subcat.nome}')
                        print(f'produto: {produto.instance.nome}')

    print('-------------------------------------')
    print('-------------------------------------')
    print('--------------DEBUGGING--------------')
    print('-------------------------------------')
    print('-------------------------------------')
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

        print(formset.is_valid())
        print(formset.is_valid())
        if formset.is_valid():
            print(f'formset is valid: {formset.is_valid()}')
            formset.save()
            print('formset saved')
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
