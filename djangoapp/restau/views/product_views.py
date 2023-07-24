from django.shortcuts import render
from restau.models import Products


PER_PAGE = 9


def index(request):
    return render(
        request,
        'restau/pages/index.html'
    )


def admin_home(request):
    produtos = Products.objects.all()
    print(produtos)
    return render(
        request,
        'restau/pages/admin-home.html',
        {'produtos': produtos},

    )
