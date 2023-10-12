from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import CategoryForm
from restau.models import Category
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def criar_categoria(request):

    categorias = Category.objects.all().order_by('ordem')

    form_action = reverse('restau:criar_categoria')

    if request.method == 'POST':

        form = CategoryForm(request.POST, request.FILES)
        context = {
            'categorias': categorias,
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            print(f'form is valid: {form.is_valid()}')
            categoria = form.save()
            print('form saved')
            return redirect(
                'restau:criar_categoria', categoria_id=categoria.id
            )

        else:
            print(f'form: {form.errors}')

        return render(
            request,
            'restau/pages/criar_categoria.html',
            context
        )

    context = {
        'categorias': categorias,
        'form': CategoryForm(),
        'form_action': form_action,
    }

    return render(
        request,
        'restau/pages/criar_categoria.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def atualizar_categoria(request, categoria_id):
    categoria = get_object_or_404(
        Category, pk=categoria_id)
    form_action = reverse('restau:atualizar_categoria', args=(categoria_id,))
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=categoria)
        context = {
            'categoria': categoria,
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            categoria = form.save()
            return redirect('restau:criar_categoria')

        return render(
            request,
            'restau/pages/criar_categoria.html',
            context
        )

    context = {
        'categoria': categoria,
        'form': CategoryForm(instance=categoria),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/criar_categoria.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def apagar_categoria(request, categoria_id):
    categoria = get_object_or_404(
        Category, pk=categoria_id
    )
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        categoria.delete()
        return redirect('restau:criar_categoria')

    return render(
        request,
        'restau/pages/categoria.html',
        {
            'categoria': categoria,
            'confirmation': confirmation,
        }
    )


def ordenar_categorias(request):
    categorias = Category.objects.all().order_by('ordem')

    CategoriaFormSet = modelformset_factory(
        Category, fields=('id', 'nome', 'ordem',), extra=0)

    formset = CategoriaFormSet(queryset=Category.objects
                               .all()
                               .order_by('ordem')
                               )
    form_action = reverse('restau:ordenar_categorias')
    if request.method == 'POST':
        formset = CategoriaFormSet(
            request.POST, request.FILES, queryset=Category.objects.all())

        context = {
            'categorias': categorias,
            'formset': formset,
            'form_action': form_action,

        }

        if formset.is_valid():
            formset.save()  # Salva o formset diretamente
            return redirect('restau:ordenar_categorias')

        else:
            print(f'formset: {formset.errors}')

        return render(
            request,
            'restau/pages/ordenar_categorias.html',
            context
        )

    context = {
        'categorias': categorias,
        'formset': formset,
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/ordenar_categorias.html',
        context,
    )
