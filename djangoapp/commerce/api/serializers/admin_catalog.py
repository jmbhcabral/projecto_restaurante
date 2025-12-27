# djangoapp/commerce/api/serializers/admin_catalog.py
from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

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

# ---------------------------
# Admin: Category / Product
# ---------------------------

class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class AdminProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "sku",
            "name",
            "description",
            "category",
            "base_price",
            "status",
            "is_sellable",
            "product_type",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


# ---------------------------
# Admin: Ingredient + Prices
# ---------------------------

class AdminIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class AdminProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ("id", "product", "price", "valid_from", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_price(self, value: Decimal) -> Decimal:
        if value < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        return value


class AdminIngredientPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientPrice
        fields = ("id", "ingredient", "price", "valid_from", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_price(self, value: Decimal) -> Decimal:
        if value < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        return value


class AdminProductDefaultIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDefaultIngredient
        fields = ("id", "product", "ingredient", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


# ---------------------------
# Admin: Add-ons (Extras)
# ---------------------------

class AdminAddOnGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOnGroup
        fields = (
            "id",
            "product",
            "name",
            "min_select",
            "max_select",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        min_select = int(attrs.get("min_select", getattr(self.instance, "min_select", 0)))
        max_select = int(attrs.get("max_select", getattr(self.instance, "max_select", 1)))
        if max_select < min_select:
            raise serializers.ValidationError({"max_select": "max_select tem de ser >= min_select."})
        return attrs


class AdminAddOnOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOnOption
        fields = (
            "id",
            "group",
            "ingredient",
            "price",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_price(self, value: Decimal) -> Decimal:
        if value < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        return value


# ---------------------------
# Admin: Product Images
# ---------------------------

class AdminProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "gcs_path", "public_url", "is_primary", "order", "created_at")
        read_only_fields = ("id", "gcs_path", "public_url", "created_at")


class AdminProductWithImagesSerializer(serializers.ModelSerializer):
    images = AdminProductImageSerializer(many=True, read_only=True)
    primary_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "sku",
            "name",
            "description",
            "category",
            "base_price",
            "status",
            "is_sellable",
            "product_type",
            "images",
            "primary_image_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_primary_image_url(self, obj: Product):
        img = obj.images.filter(is_primary=True).first()
        return img.public_url if img else None
