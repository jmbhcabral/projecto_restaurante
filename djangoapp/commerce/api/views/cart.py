from __future__ import annotations

from typing import Any, Mapping, cast

from commerce.api.permissions import IsCartOwner
from commerce.api.serializers.cart import (
    CartAddAddonInputSerializer,
    CartAddItemInputSerializer,
    CartRemoveAddonInputSerializer,
    CartRemoveDefaultIngredientInputSerializer,
    CartSerializer,
    CartUpdateItemInputSerializer,
)
from commerce.models import (
    AddOnOption,
    Cart,
    CartItem,
    CartItemAddOn,
    CartItemComboSelection,
    CartItemRemovedIngredient,
    ComboChoiceGroup,
    ComboChoiceOption,
    Product,
    ProductDefaultIngredient,
)
from commerce.services.cart_loader import load_cart
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


def get_or_create_active_cart(request) -> Cart:
    # English comments: enterprise: support authenticated + session carts
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key or ""
    if not session_key:
        request.session.save()
        session_key = request.session.session_key or ""

    cart, _ = Cart.objects.get_or_create(
        is_active=True,
        user=user,
        session_key="" if user else session_key,
        defaults={"session_key": "" if user else session_key},
    )
    return cart


def _apply_combo_selections(item: CartItem, selections: list[dict[str, Any]]) -> None:
    """
    English comments:
    - Validate selections belong to the combo
    - Enforce min/max constraints per group
    - Persist CartItemComboSelection rows
    """
    combo = item.product

    groups = (
        ComboChoiceGroup.objects
        .filter(combo=combo)
        .order_by("sort_order", "pk")
    )

    group_by_id = {g.pk: g for g in groups}
    counts: dict[int, int] = {g.pk: 0 for g in groups}

    # If combo has required groups, selections must be provided
    if groups.exists() and not selections:
        for g in groups:
            if g.min_select > 0:
                raise ValueError("Este menu requer seleções obrigatórias (ex: bebida e acompanhamento).")

    # Prevent duplicate options in payload (better than hitting DB unique constraint)
    seen_option_ids: set[int] = set()

    for s in selections:
        group_id = int(s["group_id"])
        option_id = int(s["option_id"])
        qty = int(s.get("quantity", 1))

        if qty < 1:
            raise ValueError("Seleção inválida: quantity tem de ser >= 1.")

        if option_id in seen_option_ids:
            raise ValueError("Seleção inválida: opção repetida.")
        seen_option_ids.add(option_id)

        g = group_by_id.get(group_id)
        if not g:
            raise ValueError("Seleção inválida: grupo não pertence a este combo.")

        try:
            opt = (
                ComboChoiceOption.objects
                .select_related("group", "product", "group__combo")
                .get(pk=option_id)
            )
        except ComboChoiceOption.DoesNotExist:
            raise ValueError("Seleção inválida: opção não encontrada.")

        if opt.group.pk != g.pk:
            raise ValueError("Seleção inválida: opção não pertence ao grupo.")

        if not opt.is_active:
            raise ValueError("Seleção inválida: opção inativa.")

        if opt.product.status != Product.Status.ACTIVE or not opt.product.is_sellable:
            raise ValueError("Seleção inválida: produto da opção indisponível.")

        CartItemComboSelection.objects.create(
            item=item,
            group=g,
            option=opt,
            quantity=qty,
        )
        counts[g.pk] += qty

        # Early max check (fail fast)
        if counts[g.pk] > g.max_select:
            raise ValueError(f"Selecionaste demasiado em '{g.name}'.")

    # Enforce min per group
    for g in groups:
        c = counts[g.pk]
        if c < g.min_select:
            raise ValueError(f"Falta selecionar em '{g.name}'.")


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsCartOwner]

    def retrieve(self, request, pk=None):
        cart = get_or_create_active_cart(request)
        self.check_object_permissions(request, cart)

        cart = load_cart(cart.pk)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["post"], url_path="items")
    @transaction.atomic
    def add_item(self, request):
        cart = get_or_create_active_cart(request)
        self.check_object_permissions(request, cart)

        inp = CartAddItemInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        data = cast(Mapping[str, Any], inp.validated_data)

        product_id = int(data["product_id"])
        qty = int(data["quantity"])
        note = str(data.get("note", ""))

        item = CartItem.objects.create(
            cart=cart,
            product_id=product_id,
            quantity=qty,
            note=note,
        )

        # Determine product type explicitly (small + predictable query)
        product_type = (
            Product.objects
            .only("product_type")
            .get(pk=product_id)
            .product_type
        )

        try:
            if product_type == Product.ProductType.COMBO:
                selections = list(cast(list[dict[str, Any]], data.get("selections", [])))
                _apply_combo_selections(item=item, selections=selections)
        except ValueError as e:
            raise ValidationError({"detail": str(e)})

        cart = load_cart(cart.pk)
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["patch"], url_path=r"items/(?P<item_id>\d+)")
    @transaction.atomic
    def update_item(self, request, item_id=None):
        cart = get_or_create_active_cart(request)
        self.check_object_permissions(request, cart)

        try:
            item = CartItem.objects.select_related("cart").get(pk=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        inp = CartUpdateItemInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        data = cast(Mapping[str, Any], inp.validated_data)

        for k, v in data.items():
            setattr(item, k, v)

        update_fields = list(data.keys()) + ["updated_at"]
        item.save(update_fields=update_fields)

        cart = load_cart(cart.pk)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["delete"], url_path=r"items/(?P<item_id>\d+)")
    @transaction.atomic
    def remove_item(self, request, item_id=None):
        cart = get_or_create_active_cart(request)
        self.check_object_permissions(request, cart)

        deleted, _ = CartItem.objects.filter(pk=item_id, cart=cart).delete()
        if deleted == 0:
            return Response({"detail": "Item não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        cart = load_cart(cart.pk)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["post"], url_path=r"items/(?P<item_id>\d+)/addons")
    @transaction.atomic
    def add_addon(self, request, item_id=None):
        cart = get_or_create_active_cart(request)
        self.check_object_permissions(request, cart)

        try:
            item = CartItem.objects.select_related("product").get(pk=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        inp = CartAddAddonInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        data = cast(Mapping[str, Any], inp.validated_data)

        option = AddOnOption.objects.select_related("group", "group__product").get(pk=int(data["option_id"]))

        if option.group.product.pk != item.product.pk:
            return Response({"detail": "Extra não pertence a este produto."}, status=status.HTTP_400_BAD_REQUEST)

        addon, created = CartItemAddOn.objects.get_or_create(
            item=item,
            option=option,
            defaults={"quantity": int(data["quantity"])},
        )
        if not created:
            addon.quantity += int(data["quantity"])
            addon.save(update_fields=["quantity", "updated_at"])

        cart = load_cart(cart.pk)
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["delete"], url_path=r"items/(?P<item_id>\d+)/addons")
    @transaction.atomic
    def remove_addon(self, request, item_id=None):
        cart = get_or_create_active_cart(request)
        self.check_object_permissions(request, cart)

        try:
            item = CartItem.objects.get(pk=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        inp = CartRemoveAddonInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        data = cast(Mapping[str, Any], inp.validated_data)

        deleted, _ = CartItemAddOn.objects.filter(item=item, option_id=int(data["option_id"])).delete()
        if deleted == 0:
            return Response({"detail": "Extra não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        cart = load_cart(cart.pk)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["post"], url_path=r"items/(?P<item_id>\d+)/remove-ingredient")
    @transaction.atomic
    def remove_default_ingredient(self, request, item_id=None):
        cart = get_or_create_active_cart(request)
        self.check_object_permissions(request, cart)

        try:
            item = CartItem.objects.select_related("product").get(pk=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        inp = CartRemoveDefaultIngredientInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        data = cast(Mapping[str, Any], inp.validated_data)
        ingredient_id = int(data["ingredient_id"])

        is_default = ProductDefaultIngredient.objects.filter(
            product_id=item.product.pk,
            ingredient_id=ingredient_id,
        ).exists()
        if not is_default:
            return Response({"detail": "Só podes remover ingredientes base deste produto."}, status=status.HTTP_400_BAD_REQUEST)

        CartItemRemovedIngredient.objects.get_or_create(item=item, ingredient_id=ingredient_id)

        cart = load_cart(cart.pk)
        return Response(CartSerializer(cart).data)