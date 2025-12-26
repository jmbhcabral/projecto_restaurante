# djangoapp/commerce/services/orders.py
"""
Services for orders.
"""
from __future__ import annotations

from commerce.models import Order, TicketCounter
from django.db import transaction
from django.utils import timezone


@transaction.atomic
def assign_ticket_number(order: Order) -> int:
    """
    Assigns an incremental ticket number per day with row locking.
    """
    today = timezone.localdate()
    counter, _ = TicketCounter.objects.select_for_update().get_or_create(date=today)
    n = counter.next()
    order.ticket_number = n
    order.save(update_fields=["ticket_number", "updated_at"])
    return n


@transaction.atomic
def mark_order_paid(order: Order) -> None:
    if order.status not in [Order.Status.SUBMITTED, Order.Status.DRAFT, "pending_payment"]:
        # keep it strict; adjust based on your actual enum values
        return

    order.status = "paid"
    order.paid_at = timezone.now()

    if not order.ticket_number:
        assign_ticket_number(order)

    # Source-based flow
    if order.source == Order.Source.POS:
        order.status = "confirmed"
        order.confirmed_at = timezone.now()
    else:
        order.status = "pending_confirmation"

    order.save(update_fields=["status", "paid_at", "confirmed_at", "ticket_number", "updated_at"])