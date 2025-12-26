# djangoapp/commerce/api/views/checkout.py
from __future__ import annotations

import secrets

from commerce.api.permissions import IsCartOwner

# from commerce.api.serializers.cart import CartSerializer
from commerce.api.serializers.checkout import CheckoutInputSerializer
from commerce.api.views.cart import get_or_create_active_cart
from commerce.models import (
    Order,
    OrderItem,
    OrderItemAddOn,
    OrderItemComboSelection,
    OrderItemRemovedIngredient,
)
from commerce.services.cart_loader import load_cart
from commerce.services.pricing import calc_cart_totals
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class CheckoutViewSet(viewsets.ViewSet):
    permission_classes = [IsCartOwner]

    @action(detail=False, methods=["post"], url_path="checkout")
    @transaction.atomic
    def checkout(self, request):
        cart = get_or_create_active_cart(request)
        self.check_object_permissions(request, cart)

        inp = CheckoutInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)

        cart = load_cart(cart.pk)

        if not cart.items.exists():
            return Response({"detail": "Carrinho vazio."}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = calc_cart_totals(cart)

        # generate stable public code (ticket number)
        public_code = secrets.token_hex(6).upper()

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            status=Order.Status.SUBMITTED,
            public_code=public_code,
            subtotal=subtotal,
            discounts="0.00",
            taxes="0.00",
            total=subtotal,
        )

        # Copy items + snapshots
        for ci in cart.items.all():
            oi = OrderItem.objects.create(
                order=order,
                product=ci.product,
                quantity=ci.quantity,
                unit_base_price=ci.product.base_price,
                note=ci.note,
            )

            # Add-ons snapshot
            for a in ci.addons.all():
                OrderItemAddOn.objects.create(
                    item=oi,
                    option=a.option,
                    ingredient_name=a.option.ingredient.name,
                    unit_price=a.option.price,
                    quantity=a.quantity,
                )

            # Removed ingredients snapshot (no price effect)
            for r in ci.removed_ingredients.all():
                OrderItemRemovedIngredient.objects.create(
                    item=oi,
                    ingredient_name=r.ingredient.name,
                )

            # Combo selections snapshot
            for s in ci.combo_selections.all():
                OrderItemComboSelection.objects.create(
                    item=oi,
                    group_name=s.group.name,
                    product_sku=s.option.product.sku,
                    product_name=s.option.product.name,
                    unit_price_delta=s.option.price_delta,
                    quantity=s.quantity,
                )
        # Close cart
        cart.is_active = False
        cart.save(update_fields=["is_active", "updated_at"])

        return Response(
            {
                "order": {
                    "id": order.pk,
                    "public_code": order.public_code,
                    "status": order.status,
                    "subtotal": str(order.subtotal),
                    "total": str(order.total),
                }
            },
            status=status.HTTP_201_CREATED,
        )