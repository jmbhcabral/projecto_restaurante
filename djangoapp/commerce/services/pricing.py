from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from commerce.models import Cart, CartItem, CartItemAddOn, CartItemComboSelection


@dataclass(frozen=True)
class LineTotal:
    unit: Decimal
    qty: int
    total: Decimal


def _iter_item_addons(item: CartItem):
    """
    English comments:
    - Prefer using prefetched related manager to avoid DB hits.
    - Fall back to a query if not prefetched.
    """
    mgr = item.addons
    cache = getattr(item, "_prefetched_objects_cache", {})
    if "addons" in cache:
        return mgr.all()
    return CartItemAddOn.objects.select_related("option").filter(item=item)


def _iter_item_combo_selections(item: CartItem):
    """
    English comments:
    - Prefer using prefetched related manager to avoid DB hits.
    - Fall back to a query if not prefetched.
    """
    mgr = item.combo_selections
    cache = getattr(item, "_prefetched_objects_cache", {})
    if "combo_selections" in cache:
        return mgr.all()
    return CartItemComboSelection.objects.select_related("option").filter(item=item)


def calc_cart_item_unit_price(item: CartItem) -> Decimal:
    """
    Pricing rules:
    - Base product price always counts
    - Removed ingredients never reduce price
    - Add-ons increase price (option.price * quantity)
    - Combo selections increase price (option.price_delta * quantity)
    """
    price = item.product.base_price

    # Add-ons
    for a in _iter_item_addons(item):
        # If option was prefetched via items__addons__option, this is zero extra queries.
        price += (a.option.price * a.quantity)

    # Combo selections
    for s in _iter_item_combo_selections(item):
        # If option was prefetched via items__combo_selections__option, this is zero extra queries.
        price += (s.option.price_delta * s.quantity)

    return price


def calc_cart_item_total(item: CartItem) -> LineTotal:
    unit = calc_cart_item_unit_price(item)
    qty = int(item.quantity)
    total = unit * qty
    return LineTotal(unit=unit, qty=qty, total=total)


def calc_cart_totals(cart: Cart) -> Decimal:
    """
    English comments:
    - If cart.items was prefetched, this won't hit DB for items.
    - Still safe if not prefetched.
    """
    items = cart.items.all()
    subtotal = Decimal("0.00")

    for item in items:
        subtotal += calc_cart_item_total(item).total

    return subtotal