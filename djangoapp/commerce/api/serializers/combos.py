# djangoapp/commerce/api/serializers/combos.py
from __future__ import annotations

from rest_framework import serializers

from djangoapp.commerce.models import (
    ComboChoiceGroup,
    ComboChoiceOption,
    Product,
)


class ComboChoiceOptionSerializer(serializers.ModelSerializer):
    option_id = serializers.IntegerField(source="pk", read_only=True)

    product_id = serializers.IntegerField(source="product.pk", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ComboChoiceOption
        fields = (
            "option_id",
            "product_id",
            "product_sku",
            "product_name",
            "price_delta",
            "is_active",
        )


class ComboChoiceGroupSerializer(serializers.ModelSerializer):
    group_id = serializers.IntegerField(source="pk", read_only=True)
    options = ComboChoiceOptionSerializer(many=True, read_only=True)

    class Meta:
        model = ComboChoiceGroup
        fields = (
            "group_id",
            "name",
            "min_select",
            "max_select",
            "sort_order",
            "options",
        )


class ComboListSerializer(serializers.ModelSerializer):
    # English comments: minimal fields for listing combos
    combo_id = serializers.IntegerField(source="pk", read_only=True)

    class Meta:
        model = Product
        fields = (
            "combo_id",
            "sku",
            "name",
            "description",
            "base_price",
            "is_sellable",
            "status",
        )


class ComboConfigSerializer(serializers.ModelSerializer):
    # English comments: config payload for frontend modal
    combo_id = serializers.IntegerField(source="pk", read_only=True)
    groups = ComboChoiceGroupSerializer(source="choice_groups", many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "combo_id",
            "sku",
            "name",
            "description",
            "base_price",
            "is_sellable",
            "status",
            "groups",
        )