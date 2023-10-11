from django.shortcuts import render


def configuracao(request):
    return render(
        request,
        'restau/pages/admin_configuracao.html',
    )
