# djangoapp/commerce/api/views/admin_catalog.py
from __future__ import annotations

from commerce.api.permissions import IsAccessRestricted
from commerce.api.serializers.admin_catalog import (
    AdminAddOnGroupSerializer,
    AdminAddOnOptionSerializer,
    AdminCategorySerializer,
    AdminIngredientPriceSerializer,
    AdminIngredientSerializer,
    AdminProductDefaultIngredientSerializer,
    AdminProductPriceSerializer,
    AdminProductSerializer,
)
from commerce.models import (
    AddOnGroup,
    AddOnOption,
    Category,
    Ingredient,
    IngredientPrice,
    Product,
    ProductDefaultIngredient,
    ProductPrice,
)
from rest_framework import filters, viewsets


class AdminBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAccessRestricted]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: list[str] = []
    ordering_fields: list[str] = ["pk"]
    ordering = ["-pk"]


class AdminCategoryViewSet(AdminBaseViewSet):
    serializer_class = AdminCategorySerializer
    queryset = Category.objects.all().order_by("name")
    search_fields = ["name", "slug"]
    ordering_fields = ["pk", "name", "created_at"]


class AdminProductViewSet(AdminBaseViewSet):
    serializer_class = AdminProductSerializer
    queryset = Product.objects.select_related("category").all().order_by("name")
    search_fields = ["name", "sku", "description", "category__name"]
    ordering_fields = ["pk", "name", "created_at", "base_price", "status", "product_type", "is_sellable"]


class AdminIngredientViewSet(AdminBaseViewSet):
    serializer_class = AdminIngredientSerializer
    queryset = Ingredient.objects.all().order_by("name")
    search_fields = ["name"]
    ordering_fields = ["pk", "name", "is_active", "created_at"]


class AdminProductPriceViewSet(AdminBaseViewSet):
    serializer_class = AdminProductPriceSerializer
    queryset = ProductPrice.objects.select_related("product").all().order_by("-valid_from", "-pk")
    search_fields = ["product__sku", "product__name"]
    ordering_fields = ["pk", "valid_from", "price", "created_at"]


class AdminIngredientPriceViewSet(AdminBaseViewSet):
    serializer_class = AdminIngredientPriceSerializer
    queryset = IngredientPrice.objects.select_related("ingredient").all().order_by("-valid_from", "-pk")
    search_fields = ["ingredient__name"]
    ordering_fields = ["pk", "valid_from", "price", "created_at"]


class AdminProductDefaultIngredientViewSet(AdminBaseViewSet):
    serializer_class = AdminProductDefaultIngredientSerializer
    queryset = ProductDefaultIngredient.objects.select_related("product", "ingredient").all().order_by("-pk")
    search_fields = ["product__sku", "product__name", "ingredient__name"]
    ordering_fields = ["pk", "created_at"]


class AdminAddOnGroupViewSet(AdminBaseViewSet):
    serializer_class = AdminAddOnGroupSerializer
    queryset = AddOnGroup.objects.select_related("product").all().order_by("product_id", "name")
    search_fields = ["name", "product__sku", "product__name"]
    ordering_fields = ["pk", "name", "created_at", "product"]


class AdminAddOnOptionViewSet(AdminBaseViewSet):
    serializer_class = AdminAddOnOptionSerializer
    queryset = AddOnOption.objects.select_related("group", "ingredient", "group__product").all().order_by("group_id", "pk")
    search_fields = ["group__name", "ingredient__name", "group__product__sku", "group__product__name"]
    ordering_fields = ["pk", "price", "is_active", "created_at", "group"]