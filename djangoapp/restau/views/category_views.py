from django.shortcuts import render, get_object_or_404
from restau.models import Category
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
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
