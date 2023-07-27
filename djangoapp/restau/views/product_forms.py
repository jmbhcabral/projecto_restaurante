from django.shortcuts import render, redirect
from django.urls import reverse
from restau.forms import ProductForm


def create_product(request):
    form_action = reverse('restau:create_product')
    if request.method == 'POST':
        form = ProductForm(request.POST)
        context = {
            'form': form
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
        'form': ProductForm()
    }
    return render(
        request,
        'restau/pages/create_product.html',
        context
    )
