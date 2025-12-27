from __future__ import annotations

from django.db.models import Prefetch

from djangoapp.commerce.models import Cart, CartItem


def load_cart(cart_id: int) -> Cart:
    """
    - Single source of truth for cart loading
    - Ensures serializer + pricing have all relations loaded efficiently
    """
    items_qs = (
        CartItem.objects
        .select_related("product")  # FK -> JOIN (faster, fewer queries)
        .prefetch_related(
            "addons__option__ingredient",
            "removed_ingredients__ingredient",
            "combo_selections__group",
            "combo_selections__option__product",
        )
    )

    return (
        Cart.objects
        .prefetch_related(
            Prefetch("items", queryset=items_qs),
        )
        .get(pk=cart_id)
    )