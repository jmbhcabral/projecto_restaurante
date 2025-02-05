from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import EmentaForm, ProdutosEmentaForm
from restau.models import (
    Ementa, Products, Category,
    SubCategory, ProdutosEmenta
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def criar_ementa(request):
    ementas = Ementa.objects.all().order_by('id')

    form_action = reverse('restau:criar_ementa')

    if request.method == 'POST':
        form = EmentaForm(request.POST, )
        context = {
            'ementas': ementas,
            'form': form,
            'form_action': form_action
        }
        if form.is_valid():
            form.save()
            return redirect('restau:criar_ementa')

        return render(
            request,
            'restau/pages/criar_ementa.html',
            context
        )

    context = {
        'ementas': ementas,
        'form': EmentaForm(),
        'form_action': form_action
    }

    return render(
        request,
        'restau/pages/criar_ementa.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def atualizar_ementa(request, ementa_id):
    ementa = get_object_or_404(
        Ementa, pk=ementa_id
    )
    form_action = reverse('restau:atualizar_ementa', args=(ementa_id,))
    if request.method == 'POST':
        form = EmentaForm(request.POST, instance=ementa)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            ementa = form.save()
            return redirect('restau:criar_ementa')

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
        'restau/pages/criar_ementa.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def apagar_ementa(request, ementa_id):
    ementa_para_apagar = get_object_or_404(
        Ementa, pk=ementa_id,
    )
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        ementa_para_apagar.delete()
        return redirect('restau:criar_ementa')

    return render(
        request,
        'restau/pages/ementa.html',
        {
            'ementa': ementa_para_apagar,
            'confirmation': confirmation,
        }
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(name='acesso_restrito').exists())
def povoar_ementa(request, ementa_id):
    ementa = get_object_or_404(Ementa, pk=ementa_id)

    # Buscar categorias, subcategorias e produtos ordenados
    categorias = Category.objects.all().order_by('ordem')
    subcategorias = SubCategory.objects.all().order_by('ordem')
    produtos = Products.objects.all().order_by('ordem')

    form_action = reverse('restau:povoar_ementa', args=[ementa_id])

    # Buscar produtos já associados a esta ementa e suas descrições personalizadas
    produtos_ementa = ProdutosEmenta.objects.filter(ementa=ementa)
    
    produtos_na_ementa = {pe.produto.id for pe in produtos_ementa if pe.produto}  # Set de IDs
    produtos_descricao = {pe.produto.id: pe.descricao for pe in produtos_ementa if pe.produto}  # Dicionário de descrições

    if request.method == 'POST':
        print(f'request.POST: {request.POST}')
        form = ProdutosEmentaForm(request.POST, ementa_id=ementa_id)

        if form.is_valid():
            selected_products = form.cleaned_data['produto']  # Produtos selecionados no formulário

            # Adicionar novos produtos ou atualizar descrições
            for product in selected_products:
                descricao_personalizada = request.POST.get(f'descricao_{product.id}', '')  # Obter descrição

                # Atualizar se já existir na ementa, senão criar um novo
                produtos_ementa_obj, created = ProdutosEmenta.objects.get_or_create(
                    ementa=ementa, produto=product,
                    defaults={'descricao': descricao_personalizada}
                )

                # Se já existir e a descrição foi alterada, atualizar
                if not created and produtos_ementa_obj.descricao != descricao_personalizada:
                    produtos_ementa_obj.descricao = descricao_personalizada
                    produtos_ementa_obj.save()

            # Remover produtos que foram desmarcados
            ProdutosEmenta.objects.filter(ementa=ementa).exclude(produto__in=selected_products).delete()

            messages.success(request, f"Produtos atualizados na ementa {ementa}")
            return redirect('restau:povoar_ementa', ementa_id=ementa_id)
        else:
            messages.error(request, "O formulário não é válido.")

    else:
        # Definir os produtos já presentes na ementa como os valores iniciais do formulário
        initial_products = Products.objects.filter(id__in=produtos_na_ementa)
        form = ProdutosEmentaForm(ementa_id=ementa_id, initial={'produto': initial_products})

    context = {
        'produtos_na_ementa': produtos_na_ementa,
        'produtos_descricao': produtos_descricao,  # Enviar as descrições para o template
        'ementa': ementa,
        'produtos': produtos,
        'categorias': categorias,
        'subcategorias': subcategorias,
        'form': form,
        'form_action': form_action,
    }

    return render(request, 'restau/pages/povoar_ementa.html', context)