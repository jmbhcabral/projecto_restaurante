# djangoapp/commerce/api/views/admin_catalog.py
from __future__ import annotations

from django.db import transaction
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from djangoapp.commerce.api.permissions import IsAccessRestricted
from djangoapp.commerce.api.serializers.admin_catalog import (
    AdminAddOnGroupSerializer,
    AdminAddOnOptionSerializer,
    AdminCategorySerializer,
    AdminIngredientPriceSerializer,
    AdminIngredientSerializer,
    AdminProductDefaultIngredientSerializer,
    AdminProductImageSerializer,
    AdminProductPriceSerializer,
    AdminProductWithImagesSerializer,
)
from djangoapp.commerce.models import (
    AddOnGroup,
    AddOnOption,
    Category,
    Ingredient,
    IngredientPrice,
    Product,
    ProductDefaultIngredient,
    ProductImage,
    ProductPrice,
)
from djangoapp.commerce.services.gcs_upload import upload_file_to_gcs


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
    serializer_class = AdminProductWithImagesSerializer
    queryset = Product.objects.select_related("category").prefetch_related("images").all().order_by("name")
    search_fields = ["name", "sku", "description", "category__name"]
    ordering_fields = ["pk", "name", "created_at", "base_price", "status", "product_type", "is_sellable"]

    @action(
        detail=True,
        methods=["post"],
        url_path="images",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_image(self, request, pk: str | None = None):
        
        product = self.get_object()  # pyright: ignore[reportUnboundVariable]        

        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "Missing file"}, status=status.HTTP_400_BAD_REQUEST)

        is_primary = str(request.data.get("is_primary", "false")).lower() in ("1", "true", "yes", "on")
        order = int(request.data.get("order", 0) or 0)

        result = upload_file_to_gcs(
            file_obj=file_obj,
            content_type=getattr(file_obj, "content_type", "application/octet-stream"),
            folder=f"products/{product.id}",
        )

        with transaction.atomic():
            if is_primary:
                ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)

            img = ProductImage.objects.create(
                product=product,
                gcs_path=result.gcs_path,
                public_url=result.public_url,
                is_primary=is_primary,
                order=order,
            )

        return Response(AdminProductImageSerializer(img).data, status=status.HTTP_201_CREATED)


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
