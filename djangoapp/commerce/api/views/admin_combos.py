from __future__ import annotations

from commerce.api.permissions import IsAccessRestricted
from commerce.api.serializers.admin_combos import (
    AdminComboChoiceGroupSerializer,
    AdminComboChoiceOptionSerializer,
)
from commerce.models import ComboChoiceGroup, ComboChoiceOption
from rest_framework import filters, viewsets


class AdminComboChoiceGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAccessRestricted]
    serializer_class = AdminComboChoiceGroupSerializer
    queryset = ComboChoiceGroup.objects.select_related("combo").all().order_by("combo_id", "sort_order", "pk")

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "combo__name", "combo__sku"]
    ordering_fields = ["pk", "sort_order", "created_at", "combo"]


class AdminComboChoiceOptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAccessRestricted]
    serializer_class = AdminComboChoiceOptionSerializer
    queryset = (
        ComboChoiceOption.objects
        .select_related("group", "group__combo", "product")
        .all()
        .order_by("group_id", "pk")
    )

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["group__name", "group__combo__sku", "product__name", "product__sku"]
    ordering_fields = ["pk", "created_at", "price_delta", "is_active"]