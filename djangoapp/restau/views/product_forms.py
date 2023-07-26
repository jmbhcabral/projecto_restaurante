from django.shortcuts import render
from restau.forms import ProductForm


def create_product(request):
    if request.method == 'POST':
        context = {
            'form': ProductForm(request.POST)
        }
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
