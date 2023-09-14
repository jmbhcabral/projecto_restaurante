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

    ementa = get_object_or_404(Ementa, pk=ementa_id)

    categorias = Category.objects.all().order_by('ordem')
    subcategorias = SubCategory.objects.all().order_by('ordem')
    produtos = Products.objects.all().order_by('ordem')

    form_action = reverse('restau:povoar_ementa', args=[ementa_id])

    if request.method == 'POST':
        form = ProdutosEmentaForm(request.POST, ementa_id=ementa_id)

        if form.is_valid():
            # Crie um novo objeto ProdutosEmenta, mas não o salve ainda.
            instance = form.save(commit=False)
            instance.ementa = ementa
            instance.save()  # Agora, salve-o.

            # Obtém os produtos selecionados no formulário.
            selected_products = form.cleaned_data['produto']

            # Obtém os produtos que já estão associados a esta ementa.
            existing_products = [prod.id for prod in ementa.produtos.all()]

            # Adicione novos produtos e remova os desmarcados.
            for product in selected_products:
                if product.id not in existing_products:
                    ementa.produtos.add(product)
                else:
                    messages.error(
                        request,
                        f"O produto {product} já existe na ementa {ementa}"
                    )

            for product_id in existing_products:
                if product_id not in [prod.id for prod in selected_products]:
                    ementa.produtos.remove(Products.objects.get(id=product_id))

            messages.success(
                request,
                f"Produtos adicionados à ementa {ementa}"
            )

            return redirect('restau:povoar_ementa', ementa_id=ementa_id)

        else:
            print("O formulário não é válido.")

    else:
        initial_products = ementa.produtos.all()  # Assume que este é o campo
        # ManyToMany
        form = ProdutosEmentaForm(ementa_id=ementa_id, initial={
                                  'produto': initial_products})

    produtos_na_ementa = [prod.id for prod in ementa.produtos.all()]

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
