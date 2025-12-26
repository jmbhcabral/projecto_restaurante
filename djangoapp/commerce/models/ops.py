# djangoapp/commerce/models/ops.py
from __future__ import annotations

from django.db import models

# from django.utils import timezone


class PosDevice(models.Model):
    """
    Represents a physical POS terminal at the counter.
    device_code should be treated like a secret token.
    """
    name = models.CharField(max_length=80)
    device_code = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TicketCounter(models.Model):
    """
    Ticket number counter per day. Use select_for_update() to avoid collisions.
    """
    date = models.DateField(unique=True)
    last_number = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def next(self) -> int:
        self.last_number += 1
        self.save(update_fields=["last_number", "updated_at"])
        return self.last_number


class KitchenPrinter(models.Model):
    """
    Store printer connection info (network or USB).
    """
    class Type(models.TextChoices):
        NETWORK = "network", "Network"
        USB = "usb", "USB"

    name = models.CharField(max_length=80)
    type = models.CharField(max_length=16, choices=Type.choices)
    host = models.CharField(max_length=120, blank=True, default="")  # for network
    port = models.PositiveIntegerField(default=9100)                  # common ESC/POS
    usb_vendor_id = models.CharField(max_length=32, blank=True, default="")
    usb_product_id = models.CharField(max_length=32, blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)