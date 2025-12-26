# djangoapp/commerce/models/combos.py
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from .catalog import Product, TimeStampedModel


class ComboChoiceGroup(TimeStampedModel):
    """
    Example: 'Drink', 'Side', 'Sauce'.
    Attached to a combo product.
    """
    if TYPE_CHECKING:
        pk: int

    combo = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="choice_groups")
    name = models.CharField(max_length=120)

    # selection rules
    min_select = models.PositiveIntegerField(default=0)
    max_select = models.PositiveIntegerField(default=1)

    # optional: ordering in UI
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(max_select__gte=models.F("min_select")), name="combo_group_max_gte_min"),
            models.UniqueConstraint(fields=["combo", "name"], name="uniq_combo_group_name_per_combo"),
        ]
        indexes = [
            models.Index(fields=["combo", "sort_order"]),
        ]

    def __str__(self) -> str:
        return f"{self.combo.sku} / {self.name}"


class ComboChoiceOption(TimeStampedModel):
    """
    An option inside a choice group. Points to a Product.
    price_delta allows (optional) upsell inside the combo.
    """
    if TYPE_CHECKING:
        pk: int
        
    group = models.ForeignKey(ComboChoiceGroup, on_delete=models.CASCADE, related_name="options")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    price_delta = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(price_delta__gte=0), name="combo_option_price_delta_non_negative"),
            models.UniqueConstraint(fields=["group", "product"], name="uniq_combo_option_product_per_group"),
        ]
        indexes = [models.Index(fields=["group"])]

    def clean(self):
        super().clean()
        if self.product.product_type == Product.ProductType.COMBO:
            raise ValidationError("Uma opção do combo não pode ser outro combo.")

    def __str__(self) -> str:
        return f"{self.group} -> {self.product.sku} (+{self.price_delta})"