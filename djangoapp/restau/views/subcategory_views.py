from django.shortcuts import render, get_object_or_404
from restau.models import SubCategory


def subcategory(request, subcategory_id):
    single_subcategory = get_object_or_404(
        SubCategory.objects
        .filter(pk=subcategory_id,))

    context = {
        'subcategory': single_subcategory,
    }

    return render(
        request,
        'restau/pages/subcategory.html',
        context,

    )
