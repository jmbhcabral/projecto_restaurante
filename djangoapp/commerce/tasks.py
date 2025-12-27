from __future__ import annotations

from celery import shared_task  # type: ignore

from djangoapp.commerce.models import Order


@shared_task
def print_kitchen_ticket(order_id: int) -> None:
    """
    English comments: I/O heavy. Fetch order, render ESC/POS payload, send to printer.
    """
    order = (
        Order.objects
        .select_related()
        .prefetch_related("items", "items__addons", "items__removed_ingredients")
        .get(pk=order_id)
    )

    # TODO: build ticket lines (text), then send via network/USB.
    # Keep retries, and log failures.