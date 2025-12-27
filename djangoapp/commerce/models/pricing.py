# djangoapp/commerce/models/pricing.py
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.db.models import Q

from djangoapp.commerce.models.catalog import Ingredient, Product, TimeStampedModel


class AddOnGroup(TimeStampedModel):
    """
    Example: "Extras", "Molhos", "Queijos".
    Can be attached to products.
    """
    name = models.CharField(max_length=120)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="addon_groups")

    # rules
    min_select = models.PositiveIntegerField(default=0)
    max_select = models.PositiveIntegerField(default=10)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(max_select__gte=models.F("min_select")),
                name="addon_group_max_gte_min",
            ),
            models.UniqueConstraint(
                fields=["product", "name"],
                name="uniq_addon_group_name_per_product",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product.sku} / {self.name}"


class AddOnOption(TimeStampedModel):
    """
    An option inside a group. Usually maps to an ingredient (e.g. extra cheese),
    but we store a price snapshot here for stability and control.
    """
    group = models.ForeignKey(AddOnGroup, on_delete=models.CASCADE, related_name="options")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)

    # price delta for selecting this option (>= 0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(price__gte=0), name="addon_option_price_non_negative"),
            models.UniqueConstraint(
                fields=["group", "ingredient"],
                name="uniq_addon_ingredient_per_group",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.group} -> {self.ingredient.name} (+{self.price})"