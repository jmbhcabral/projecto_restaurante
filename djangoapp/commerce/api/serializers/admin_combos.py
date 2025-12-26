# djangoapp/commerce/api/serializers/admin_combos.py
from __future__ import annotations

from decimal import Decimal

from commerce.models import ComboChoiceGroup, ComboChoiceOption, Product
from rest_framework import serializers

# ---------------------------
# Admin: Combos (Groups/Options)
# ---------------------------

class AdminComboChoiceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComboChoiceGroup
        fields = (
            "id",
            "combo",
            "name",
            "min_select",
            "max_select",
            "sort_order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_combo(self, value: Product) -> Product:
        if value.product_type != Product.ProductType.COMBO:
            raise serializers.ValidationError("O produto selecionado não é um combo.")
        return value

    def validate(self, attrs):
        min_select = int(attrs.get("min_select", getattr(self.instance, "min_select", 0)))
        max_select = int(attrs.get("max_select", getattr(self.instance, "max_select", 1)))
        if max_select < min_select:
            raise serializers.ValidationError({"max_select": "max_select tem de ser >= min_select."})
        return attrs


class AdminComboChoiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComboChoiceOption
        fields = (
            "id",
            "group",
            "product",
            "price_delta",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_price_delta(self, value: Decimal) -> Decimal:
        if value < 0:
            raise serializers.ValidationError("price_delta não pode ser negativo.")
        return value

    def validate(self, attrs):
        product: Product = attrs.get("product") or getattr(self.instance, "product")
        if product.status != Product.Status.ACTIVE or not product.is_sellable:
            raise serializers.ValidationError(
                {"product": "Produto da opção está indisponível (inactive ou not sellable)."}
            )
        return attrs