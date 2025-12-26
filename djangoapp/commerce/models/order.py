# djangoapp/commerce/models/order.py
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q

from .catalog import Product, TimeStampedModel
from .pricing import AddOnOption


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    class Source(models.TextChoices):
        POS = "pos", "POS"
        MOBILE = "mobile", "Mobile"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)

    # totals snapshot
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discounts = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    public_code = models.CharField(max_length=32, unique=True)  # ticket/order code for customer

    source = models.CharField(max_length=16, choices=Source.choices, default=Source.POS)
    ticket_number = models.PositiveIntegerField(null=True, blank=True)  # assigned when paid (recommended)

    pos_device = models.ForeignKey("commerce.PosDevice", null=True, blank=True, on_delete=models.SET_NULL)
    customer_ref = models.CharField(max_length=120, blank=True, default="")  # token/uid/email/whatever (your choice)

    paid_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    kitchen_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(total__gte=0), name="order_total_non_negative"),
        ]

    def __str__(self) -> str:
        return f"Order {self.public_code} ({self.status})"


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField(default=1)

    # snapshot of product base price at purchase time
    unit_base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    note = models.CharField(max_length=280, blank=True, default="")

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(quantity__gte=1), name="order_item_qty_gte_1"),
        ]


class OrderItemAddOn(TimeStampedModel):
    item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="addons")

    # keep reference (optional but useful)
    option = models.ForeignKey(AddOnOption, null=True, blank=True, on_delete=models.SET_NULL)

    # snapshot fields (enterprise: do not depend on current catalog pricing)
    ingredient_name = models.CharField(max_length=120)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(unit_price__gte=0), name="order_addon_price_non_negative"),
            models.CheckConstraint(check=Q(quantity__gte=1), name="order_addon_qty_gte_1"),
        ]


class OrderItemRemovedIngredient(TimeStampedModel):
    item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="removed_ingredients")
    ingredient_name = models.CharField(max_length=120)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["item", "ingredient_name"], name="uniq_order_item_removed_ingredient_name"),
        ]

class OrderItemComboSelection(TimeStampedModel):
    """
    Snapshot of combo selections at purchase time.
    """
    item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="combo_selections")

    group_name = models.CharField(max_length=120)
    product_sku = models.CharField(max_length=64)
    product_name = models.CharField(max_length=200)

    unit_price_delta = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(unit_price_delta__gte=0), name="order_combo_sel_price_delta_non_negative"),
            models.CheckConstraint(check=Q(quantity__gte=1), name="order_combo_sel_qty_gte_1"),
        ]