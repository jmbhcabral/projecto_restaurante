from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import SubCategoryForm
from restau.models import Category, SubCategory
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def criar_subcategoria(request):
    form_action = reverse('restau:criar_subcategoria')
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES)

        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            subcategoria = form.save()
            return redirect('restau:atualizar_subcategoria',
                            subcategoria_id=subcategoria.id)

        else:
            print(f'form: {form.errors}')

        return render(
            request,
            'restau/pages/criar_subcategoria.html',
            context
        )

    context = {
        'form': SubCategoryForm(),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/criar_subcategoria.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def atualizar_subcategoria(request, subcategoria_id):
    subcategoria = get_object_or_404(
        SubCategory, pk=subcategoria_id)
    form_action = reverse('restau:atualizar_subcategoria',
                          args=(subcategoria_id,))
    if request.method == 'POST':
        form = SubCategoryForm(
            request.POST, request.FILES, instance=subcategoria)
        context = {
            'subcategoria': subcategoria,
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            subcategoria = form.save()
            return redirect('restau:criar_subcategoria',)

        return render(
            request,
            'restau/pages/criar_subcategoria.html',
            context
        )

    context = {
        'form': SubCategoryForm(instance=subcategoria),
        'form_action': form_action,
        'subcategoria': subcategoria,
    }
    return render(
        request,
        'restau/pages/criar_subcategoria.html',
        context
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def apagar_subcategoria(request, subcategoria_id):
    subcategoria = get_object_or_404(
        SubCategory, pk=subcategoria_id
    )
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        subcategoria.delete()
        return redirect('restau:criar_subcategoria',)

    return render(
        request,
        'restau/pages/subcategoria.html',
        {
            'subcategoria': subcategoria,
            'confirmation': confirmation,
        }
    )


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def ordenar_subcategorias(request):

    CategoriaFormSet = modelformset_factory(
        Category, fields=('id', 'nome', 'ordem',), extra=0)

    SubCategoriaFormSet = modelformset_factory(
        SubCategory, fields=('id', 'nome', 'ordem', 'categoria',), extra=0)

    formset = CategoriaFormSet(queryset=Category.objects
                               .all()
                               .order_by('ordem')
                               )

    subformset = SubCategoriaFormSet(queryset=SubCategory.objects
                                     .select_related('categoria')
                                     .order_by('ordem')
                                     )

    form_action = reverse('restau:ordenar_subcategorias')

    if request.method == 'POST':
        formset = CategoriaFormSet(
            request.POST, request.FILES, queryset=Category.objects.all())

        subformset = SubCategoriaFormSet(
            request.POST, request.FILES, queryset=SubCategory.objects
            .all())

        context = {
            'formset': formset,
            'subformset': subformset,
            'form_action': form_action,
        }

        if subformset.is_valid():
            subformset.save()  # Salva o formset diretamente
            return redirect('restau:ordenar_subcategorias',)

        else:
            print(f'formset: {formset.errors}')
            print(f'Subformset: {subformset.errors}')

        return render(
            request,
            'restau/pages/ordenar_subcategorias.html',
            context
        )

    context = {
        'formset': formset,
        'subformset': subformset,
        'form_action': form_action,
    }

    return render(
        request,
        'restau/pages/ordenar_subcategorias.html',
        context
    )
