from django.shortcuts import render
from restau.forms import ProductForm


def create_product(request):
    context = {
        'form': ProductForm
    }
    return render(
        request,
        'restau/pages/create_product.html',
        context
    )
