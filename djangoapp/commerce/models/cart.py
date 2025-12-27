# djangoapp/commerce/models/cart.py
from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.db.models import Q

from djangoapp.commerce.models.catalog import Ingredient, Product, TimeStampedModel
from djangoapp.commerce.models.combos import ComboChoiceGroup, ComboChoiceOption
from djangoapp.commerce.models.pricing import AddOnOption

if TYPE_CHECKING:
    from django.db.models.manager import Manager


class Cart(TimeStampedModel):
    """
    In enterprise setups, carts can be:
    - user-based (authenticated)
    - session-based (anonymous)
    Here we support both.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=120, blank=True, default="")
    is_active = models.BooleanField(default=True)
    
    if TYPE_CHECKING:
        items: Manager["CartItem"]

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["session_key", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"Cart {self.pk}"


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    note = models.CharField(max_length=280, blank=True, default="")  # kitchen note
    
    if TYPE_CHECKING:
        addons: Manager["CartItemAddOn"]
        removed_ingredients: Manager["CartItemRemovedIngredient"]
        combo_selections: Manager["CartItemComboSelection"]

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(quantity__gte=1), name="cart_item_qty_gte_1"),
        ]

    def __str__(self) -> str:
        return f"{self.cart.id} - {self.product.sku} x{self.quantity}"


class CartItemAddOn(TimeStampedModel):
    item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name="addons")
    option = models.ForeignKey(AddOnOption, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(quantity__gte=1), name="cart_addon_qty_gte_1"),
            models.UniqueConstraint(fields=["item", "option"], name="uniq_cart_item_addon"),
        ]

    def __str__(self) -> str:
        return f"{self.item.id} + {self.option.id} x{self.quantity}"


class CartItemRemovedIngredient(TimeStampedModel):
    """
    Removing a default ingredient does NOT change price, but must be recorded.
    """
    item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name="removed_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["item", "ingredient"], name="uniq_cart_item_removed_ingredient"),
        ]

    def __str__(self) -> str:
        return f"{self.item.id} - {self.ingredient.name}"


class CartItemComboSelection(TimeStampedModel):
    """
    Stores selections for combo items.
    One row per selected option (per cart item).
    """
    item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name="combo_selections")
    group = models.ForeignKey(ComboChoiceGroup, on_delete=models.PROTECT)
    option = models.ForeignKey(ComboChoiceOption, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(quantity__gte=1), name="cart_combo_sel_qty_gte_1"),
            models.UniqueConstraint(fields=["item", "option"], name="uniq_cart_combo_item_option"),
        ]

    def __str__(self) -> str:
        return f"{self.item.id} / {self.group.name} -> {self.option.product.sku} x{self.quantity}"