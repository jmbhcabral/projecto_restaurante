from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import ProductForm
from restau.models import Products


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
