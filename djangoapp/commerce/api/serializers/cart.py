# djangoapp/commerce/api/serializers/cart.py
from __future__ import annotations

from rest_framework import serializers

from djangoapp.commerce.models import (
    AddOnOption,
    Cart,
    CartItem,
    CartItemAddOn,
    CartItemComboSelection,
    CartItemRemovedIngredient,
    Ingredient,
    Product,
)
from djangoapp.commerce.services.pricing import calc_cart_item_total, calc_cart_totals

# ---------------------------
# Read serializers
# ---------------------------

class CartItemAddOnSerializer(serializers.ModelSerializer):
    option_id = serializers.IntegerField(source="option.pk", read_only=True)
    name = serializers.CharField(source="option.ingredient.name", read_only=True)
    unit_price = serializers.DecimalField(source="option.price", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItemAddOn
        fields = ("id", "option_id", "name", "unit_price", "quantity")


class CartItemRemovedIngredientSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.IntegerField(source="ingredient.pk", read_only=True)
    name = serializers.CharField(source="ingredient.name", read_only=True)

    class Meta:
        model = CartItemRemovedIngredient
        fields = ("id", "ingredient_id", "name")


class CartItemComboSelectionSerializer(serializers.ModelSerializer):
    group_id = serializers.IntegerField(source="group.pk", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    option_id = serializers.IntegerField(source="option.pk", read_only=True)
    option_product_id = serializers.IntegerField(source="option.product.pk", read_only=True)
    option_product_sku = serializers.CharField(source="option.product.sku", read_only=True)
    option_product_name = serializers.CharField(source="option.product.name", read_only=True)

    price_delta = serializers.DecimalField(source="option.price_delta", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItemComboSelection
        fields = (
            "id",
            "group_id",
            "group_name",
            "option_id",
            "option_product_id",
            "option_product_sku",
            "option_product_name",
            "price_delta",
            "quantity",
        )


class CartItemSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_type = serializers.CharField(source="product.product_type", read_only=True)

    addons = CartItemAddOnSerializer(many=True, read_only=True)
    removed_ingredients = CartItemRemovedIngredientSerializer(many=True, read_only=True)
    combo_selections = CartItemComboSelectionSerializer(many=True, read_only=True)

    unit_price = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "product_sku",
            "product_name",
            "product_type",
            "quantity",
            "note",
            "addons",
            "removed_ingredients",
            "combo_selections",
            "unit_price",
            "line_total",
            "created_at",
        )

    def get_unit_price(self, obj: CartItem) -> str:
        lt = calc_cart_item_total(obj)
        return str(lt.unit)

    def get_line_total(self, obj: CartItem) -> str:
        lt = calc_cart_item_total(obj)
        return str(lt.total)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("id", "is_active", "created_at", "items", "subtotal")

    def get_subtotal(self, obj: Cart) -> str:
        return str(calc_cart_totals(obj))


# ---------------------------
# Write serializers (commands)
# ---------------------------

class ComboSelectionInputSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    option_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartAddItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    note = serializers.CharField(required=False, allow_blank=True, default="")

    # NEW: only used when product is a combo
    selections = ComboSelectionInputSerializer(many=True, required=False, default=list)

    def validate(self, attrs):
        product_id = attrs.get("product_id")
        selections = attrs.get("selections", [])

        p = Product.objects.get(pk=product_id)

        if p.product_type == Product.ProductType.COMBO and not selections:
            raise serializers.ValidationError({"selections": "Este menu requer seleções."})

        if p.product_type != Product.ProductType.COMBO and selections:
            raise serializers.ValidationError({"selections": "Só podes enviar seleções para produtos do tipo combo."})

        return attrs
    
    def validate_product_id(self, value: int) -> int:
        # English comments: ensure product exists and is sellable
        try:
            p = Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produto inválido.")
        if not p.is_sellable or p.status != "active":
            raise serializers.ValidationError("Produto indisponível.")
        return value


class CartUpdateItemInputSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=False)
    note = serializers.CharField(required=False, allow_blank=True)


class CartAddAddonInputSerializer(serializers.Serializer):
    option_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_option_id(self, value: int) -> int:
        if not AddOnOption.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Extra inválido.")
        return value


class CartRemoveAddonInputSerializer(serializers.Serializer):
    option_id = serializers.IntegerField()


class CartRemoveDefaultIngredientInputSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField()

    def validate_ingredient_id(self, value: int) -> int:
        if not Ingredient.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Ingrediente inválido.")
        return value