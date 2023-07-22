from django.shortcuts import render


def index(request):
    return render(
        request,
        'restau/pages/index.html'
    )


def adminsetup(request):
    return render(
        request,
        'restau/pages/adminsetup.html',
    )
