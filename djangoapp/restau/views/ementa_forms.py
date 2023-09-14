from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import EmentaForm, ProdutosEmentaForm
from restau.models import (
    Ementa, Products, ProdutosEmenta, Category,
    SubCategory
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages


def ementas_create(request):
    ementas = Ementa.objects \
        .filter(nome__isnull=False) \
        .all() \
        .order_by('id')

    form_action = reverse('restau:ementas_create')

    if request.method == 'POST':
        form = EmentaForm(request.POST, )
        context = {
            'ementas': ementas,
            'form': form,
            'form_action': form_action
        }
        if form.is_valid():
            form.save()
            return redirect('restau:ementas_create')

        return render(
            request,
            'restau/pages/ementas_create.html',
            context
        )

    context = {
        'ementas': ementas,
        'form': EmentaForm(),
        'form_action': form_action
    }

    return render(
        request,
        'restau/pages/ementas.html',
        context
    )


def ementas_update(request, ementa_id):
    ementa = get_object_or_404(
        Ementa, pk=ementa_id
    )
    form_action = reverse('restau:ementas_update', args=(ementa_id,))
    if request.method == 'POST':
        form = EmentaForm(request.POST, instance=ementa)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            ementa = form.save()
            return redirect('restau:ementas_create')

        return render(
            request,
            'restau/pages/ementas.html',
            context
        )

    context = {
        'form': EmentaForm(instance=ementa),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/ementas.html',
        context
    )


def ementas_delete(request, ementa_id):
    ementa_para_apagar = get_object_or_404(
        Ementa, pk=ementa_id,
    )
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        ementa_para_apagar.delete()
        return redirect('restau:ementas_create')

    return render(
        request,
        'restau/pages/ementa.html',
        {
            'ementa': ementa_para_apagar,
            'confirmation': confirmation,
        }
    )


def povoar_ementa(request, ementa_id):
    print('REQUEST: ', request.POST)
    print("Estou aqui!")  # Isso deve ser impresso sempre que a view for chamada
    # Isso vai imprimir o método HTTP da requisição
    print("Método HTTP:", request.method)

    ementa = get_object_or_404(Ementa, pk=ementa_id)

    categorias = Category.objects.all().order_by('ordem')
    subcategorias = SubCategory.objects.all().order_by('ordem')
    produtos = Products.objects.all().order_by('ordem')
    produtos_na_ementa = ProdutosEmenta.objects.filter(
        ementa=ementa).values_list('produto', flat=True)

    form_action = reverse('restau:povoar_ementa', args=[ementa_id])
    if request.method == 'POST':
        form = ProdutosEmentaForm(request.POST or None, ementa_id=ementa_id)
        print("Formulário POST recebido")
        print(request.POST)
        import pdb
        pdb.set_trace()
        try:
            valid = form.is_valid()
            print(valid)
        except Exception as e:
            print("Erro durante a validação: ", e)

        if form.is_valid():

            print('Formulário é válido.')

            ementa = form.cleaned_data['ementa']
            print("Ementa: ", ementa)

            selected_products = form.cleaned_data['produto']
            print("Selected products: ", selected_products)

            current_products = list(
                ProdutosEmenta.objects.filter(ementa=ementa).values_list(
                    'produto', flat=True
                )
            )

            for product in form.cleaned_data['produto']:
                if not ProdutosEmenta.objects.filter(ementa=ementa, produto=product).exists():
                    ProdutosEmenta.objects.create(
                        ementa=ementa, produto=product)
                else:
                    messages.error(
                        request,
                        f"O produto {product.nome} já está na ementa {ementa.nome}."
                    )

            for product_id in current_products:
                if product_id not in [
                        product.id for product in selected_products]:
                    ProdutosEmenta.objects.filter(
                        ementa=ementa, produto_id=product_id).delete()
            return redirect('restau:povoar_ementa', ementa_id=ementa_id)
        else:
            print("O formulário não é válido.")
            print(form.errors)

        context = {
            'produtos_na_ementa': produtos_na_ementa,
            'form': form,
            'form_action': form_action,
            'ementa': ementa,
            'produtos': produtos,
            'categorias': categorias,
            'subcategorias': subcategorias,
        }
        return render(request, 'restau/pages/povoar_ementa.html', context)

    else:
        print("Não foi uma solicitação POST.")
        form = ProdutosEmentaForm(ementa_id=ementa_id)

    context = {
        'produtos_na_ementa': produtos_na_ementa,
        'ementa': ementa,
        'produtos': produtos,
        'categorias': categorias,
        'subcategorias': subcategorias,
        'form': form,
        'form_action': form_action,
    }

    return render(request, 'restau/pages/povoar_ementa.html', context)
