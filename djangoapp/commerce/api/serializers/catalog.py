# djangoapp/commerce/api/serializers/catalog.py
from __future__ import annotations

from commerce.models import Category, Product
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "sku",
            "name",
            "description",
            "base_price",
            "status",
            "is_sellable",
            "product_type",
            "category",
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "sku",
            "name",
            "description",
            "base_price",
            "status",
            "is_sellable",
            "product_type",
            "category",
            "created_at",
            "updated_at",
        )


