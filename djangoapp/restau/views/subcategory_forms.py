from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import SubCategoryForm
from restau.models import Category, SubCategory
from django.forms import modelformset_factory


def create_subcategory(request):
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

    form_action = reverse('restau:create_subcategory')

    if request.method == 'POST':
        formset = CategoriaFormSet(
            request.POST, request.FILES, queryset=Category.objects.all())

        subformset = SubCategoriaFormSet(
            request.POST, request.FILES, queryset=SubCategory.objects
            .all())

        form = SubCategoryForm(request.POST, request.FILES)
        context = {
            'formset': formset,
            'subformset': subformset,
            'form': form,
            'form_action': form_action,
        }

        if subformset.is_valid():
            print(f'Subformset is valid: {subformset.is_valid()}')
            subformset.save()  # Salva o formset diretamente
            print('Subformset saved')
            return redirect('restau:create_subcategory',)

        if form.is_valid():
            print(f'form is valid: {form.is_valid()}')
            subcategoria = form.save()
            print('form saved')
            return redirect('restau:create_subcategory',
                            subcategory_id=subcategoria.id)

        # if formset.is_valid():
        #     print(f'formset is valid: {formset.is_valid()}')
        #     formset.save()  # Salva o formset diretamente
        #     print('formset saved')
        #     return redirect('restau:create_category',)

        else:
            print(f'formset: {formset.errors}')
            print(f'Subformset: {subformset.errors}')
            print(f'form: {form.errors}')

        return render(
            request,
            'restau/pages/create_subcategory.html',
            context
        )

    context = {
        'formset': formset,
        'subformset': subformset,
        'form': SubCategoryForm(),
        'form_action': form_action,
    }
    print('-------------------------------------')
    print('-------------Debugging---------------')
    print('-------------------------------------')
    print('-------------------------------------')
    print(context)
    return render(
        request,
        'restau/pages/create_subcategory.html',
        context
    )


def update_subcategories(request, subcategory_id):
    subcategory = get_object_or_404(
        SubCategory, pk=subcategory_id)
    form_action = reverse('restau:update_subcategories',
                          args=(subcategory_id,))
    if request.method == 'POST':
        form = SubCategoryForm(
            request.POST, request.FILES, instance=subcategory)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            subcategory = form.save()
            return redirect('restau:create_subcategory')

        return render(
            request,
            'restau/pages/create_subcategory.html',
            context
        )

    context = {
        'form': SubCategoryForm(instance=subcategory),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/create_subcategory.html',
        context
    )


def delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(
        SubCategory, pk=subcategory_id
    )
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        subcategory.delete()
        return redirect('restau:create_subcategory')

    return render(
        request,
        'restau/pages/subcategory.html',
        {
            'subcategory': subcategory,
            'confirmation': confirmation,
        }
    )
