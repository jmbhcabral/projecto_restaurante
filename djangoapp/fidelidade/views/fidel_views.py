from django.shortcuts import render


def fidelidade(request):

    return render(
        request,
        'fidelidade/pages/fidelidade.html',
    )
