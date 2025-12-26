# djangoapp/commerce/api/serializers/checkout.py
from __future__ import annotations

from rest_framework import serializers


class CheckoutInputSerializer(serializers.Serializer):
    # keep minimal now; later add payments, delivery, etc.
    client_note = serializers.CharField(required=False, allow_blank=True, default="")