from django.shortcuts import render
from restau.forms import ProductForm


def create_product(request):
    context = {

    }
    return render(
        request,
        'restau/pages/create_product.html',
        context
    )
