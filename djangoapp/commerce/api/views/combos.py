# djangoapp/commerce/api/views/combos.py
from __future__ import annotations

from commerce.api.serializers.combos import ComboConfigSerializer, ComboListSerializer
from commerce.models import ComboChoiceGroup, ComboChoiceOption, Product
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class ComboViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only combos API.

    - GET /api/commerce/combos/
    - GET /api/commerce/combos/{id}/
    - GET /api/commerce/combos/{id}/config/
    """

    def get_queryset(self):
        return (
            Product.objects
            .filter(product_type=Product.ProductType.COMBO)
            .order_by("name")
        )

    def get_serializer_class(self):
        if self.action in {"retrieve", "config"}:
            return ComboConfigSerializer
        return ComboListSerializer

    def _load_combo(self, combo_id: int) -> Product:
        # English comments: single source of truth for loading combo config
        groups_qs = ComboChoiceGroup.objects.order_by("sort_order", "pk")
        options_qs = ComboChoiceOption.objects.select_related("product").order_by("pk")

        return get_object_or_404(
            Product.objects
            .filter(product_type=Product.ProductType.COMBO)
            .prefetch_related(
                Prefetch("choice_groups", queryset=groups_qs),
                Prefetch("choice_groups__options", queryset=options_qs),
            ),
            pk=combo_id,
        )

    def retrieve(self, request, *args, **kwargs):
        combo = self._load_combo(int(kwargs["pk"]))
        return Response(ComboConfigSerializer(combo).data)

    @action(detail=True, methods=["get"], url_path="config")
    def config(self, request, pk=None):
        combo = self._load_combo(int(pk or 0))
        return Response(ComboConfigSerializer(combo).data)