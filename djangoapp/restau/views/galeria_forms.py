from restau.forms import FotosForm, FotosFormSet
from restau.models import Fotos
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages


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


def povoar_galeria(request):
    # fotos = Fotos.objects.all().order_by('id')

    form_action = reverse('restau:povoar_galeria')

    if request.method == 'POST':
        print('request.POST: ', request.POST)
        formset = FotosFormSet(
            request.POST,
            request.FILES,
            queryset=Fotos.objects.all().order_by('ordem'))
        if formset.is_valid():
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    if 'DELETE' in form.changed_data:
                        messages.success(
                            request, 'Foto apagada com sucesso!')
                        # supondo que você queira deletar o registro
                        instance.delete()
                        continue
                    elif 'is_visible' in form.changed_data:
                        if instance.is_visible:
                            messages.success(
                                request, 'Foto publicada com sucesso!')
                        else:
                            messages.success(
                                request, 'Foto ocultada com sucesso!')
                    elif 'ordem' in form.changed_data:
                        messages.success(
                            request, 'Foto reordenada com sucesso!')

                    instance.save()

            return redirect('restau:povoar_galeria')

        else:
            print('formset is not valid')
            print('formset.errors: ', formset.errors)

        context = {
            'form_action': form_action,
            'formset': formset,
        }

    else:
        formset = FotosFormSet(queryset=Fotos.objects.all().order_by('ordem'))
        context = {
            'formset': formset,
        }

    return render(
        request,
        'restau/pages/povoar_galeria.html',
        context
    )
