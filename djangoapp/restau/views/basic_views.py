from django.shortcuts import render


def admin_home(request):

    return render(
        request,
        'restau/pages/admin_home.html',


    )
