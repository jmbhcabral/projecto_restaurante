# djangoapp/commerce/api/views/catalog.py
from __future__ import annotations

from django.db.models import Q, QuerySet
from rest_framework import viewsets

from djangoapp.commerce.api.serializers.catalog import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)
from djangoapp.commerce.models import Category, Product


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public read-only categories.
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("name")


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public read-only product catalog.

    Filters supported:
    - category (id) -> ?category=3
    - category_slug -> ?category_slug=burgers
    - product_type -> ?product_type=single|combo
    - sellable_only -> ?sellable_only=1 (default = 1)
    - q -> ?q=cheese
    """
    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self) -> QuerySet[Product]:
        qs = Product.objects.select_related("category").order_by("name")
        params = self.request.GET

        # English comments: default to only sellable + active products
        sellable_only = params.get("sellable_only", "1")
        if str(sellable_only).lower() in {"1", "true", "yes"}:
            qs = qs.filter(is_sellable=True, status=Product.Status.ACTIVE)

        category_id = params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)

        category_slug = params.get("category_slug")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        product_type = params.get("product_type")
        if product_type:
            qs = qs.filter(product_type=product_type)

        q = params.get("q")
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(sku__icontains=q)
            )

        return qs