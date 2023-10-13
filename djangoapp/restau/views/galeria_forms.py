from restau.forms import FotosForm
from restau.models import Fotos
from django.shortcuts import render, redirect
from django.urls import reverse


def adicionar_foto(request):
    fotos = Fotos.objects.all().order_by('id')

    form_action = reverse('restau:adicionar_foto')

    if request.method == 'POST':
        form = FotosForm(request.POST, request.FILES)
        context = {
            'fotos': fotos,
            'form': form,
            'form_action': form_action
        }
        if form.is_valid():
            form.save()
            return redirect('restau:adicionar_foto')

        return render(
            request,
            'restau/pages/adicionar_foto.html',
            context
        )

    context = {
        'fotos': fotos,
        'form': FotosForm(),
        'form_action': form_action
    }

    return render(
        request,
        'restau/pages/adicionar_foto.html',
        context
    )
