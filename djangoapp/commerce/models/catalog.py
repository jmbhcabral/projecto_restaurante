# djangoapp/commerce/models/catalog.py
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    def __str__(self):
        return self.name

class Product(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    class ProductType(models.TextChoices):
        SINGLE = 'single', 'Single'
        COMBO = 'combo', 'Combo'

    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    # Store price as Decimal to avoid floating point precision issues
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    is_sellable = models.BooleanField(default=True)
    
    product_type = models.CharField(
        max_length=16,
        choices=ProductType.choices,
        default=ProductType.SINGLE,
    )
    def __str__(self) -> str:
        return f"{self.name} - {self.sku}"


class ProductComponent(TimeStampedModel):
    """
    Fixed components for combos/packs (BOM).
    parent = combo product
    component = product included by default (fixed)
    """
    parent = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="components")
    component = models.ForeignKey("Product", on_delete=models.PROTECT, related_name="used_in_combos")

    quantity = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(quantity__gte=1), name="combo_component_qty_gte_1"),
            models.UniqueConstraint(fields=["parent", "component"], name="uniq_combo_component"),
        ]

    def __str__(self) -> str:
        return f"{self.parent.sku} includes {self.component.sku} x{self.quantity}"


class Ingredient(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)  

    def __str__(self):
        return self.name


class IngredientPrice(TimeStampedModel):
    """
    Price history for an ingredient.
    We pick the latest price where valid_from <= now (or cart.created_at).
    """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="prices")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    valid_from = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(price__gte=0),
                name="ingredient_price_non_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["ingredient", "-valid_from"]),
        ]

    def __str__(self) -> str:
        return f"{self.ingredient.name} @ {self.price} (from {self.valid_from})"


class ProductDefaultIngredient(TimeStampedModel):
    """
    Ingredients included by default in the product.
    If the user removes one: price does NOT change, but we store that choice.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="default_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "ingredient"],
                name="uniq_default_ingredient_per_product",
            )
        ]

    def __str__(self) -> str:
        return f"{self.product.sku} includes {self.ingredient.name}"


class ProductPrice(TimeStampedModel):
    """
    - Stores price history for a product
    - Only one active price at a time
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="prices"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["product", "-valid_from"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name="product_price_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product.sku} @ {self.price} (from {self.valid_from})"