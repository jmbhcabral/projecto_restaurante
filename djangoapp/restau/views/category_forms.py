from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from restau.forms import CategoryForm
from restau.models import Category


def create_category(request):
    categorias = Category.objects \
        .order_by('id')

    form_action = reverse('restau:create_category')
    print("Form Action:", form_action)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            categoria = form.save()
            return redirect('restau:create_category',
                            category_id=categoria.id)

        return render(
            request,
            'restau/pages/create_category.html',
            context
        )

    context = {
        'categorias': categorias,
        'form': CategoryForm(),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/create_category.html',
        context
    )


def update_categories(request, category_id):
    category = get_object_or_404(
        Category, pk=category_id)
    form_action = reverse('restau:update_categories', args=(category_id,))
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        context = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            category = form.save()
            return redirect('restau:create_category')

        return render(
            request,
            'restau/pages/create_category.html',
            context
        )

    context = {
        'form': CategoryForm(instance=category),
        'form_action': form_action,
    }
    return render(
        request,
        'restau/pages/create_category.html',
        context
    )


def delete_category(request, category_id):
    category = get_object_or_404(
        Category, pk=category_id
    )
    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        category.delete()
        return redirect('restau:create_category')

    return render(
        request,
        'restau/pages/category.html',
        {
            'category': category,
            'confirmation': confirmation,
        }
    )
