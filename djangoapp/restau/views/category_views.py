from django.shortcuts import render, get_object_or_404
from restau.models import Category


def category(request, category_id):
    single_category = get_object_or_404(
        Category.objects
        .filter(pk=category_id,))

    context = {
        'category': single_category,
    }

    return render(
        request,
        'restau/pages/category.html',
        context,

    )
