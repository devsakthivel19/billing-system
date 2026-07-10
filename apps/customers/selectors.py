"""Read/query helpers for customers."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.billing.models import Invoice


def get_customer_invoices(email: str) -> QuerySet[Invoice]:
    """Return invoices for customer emails matching search text.

    Args:
        email: Customer email search text.

    Returns:
        QuerySet of invoices for matching customers.
    """
    return (
        Invoice.objects.select_related("customer")
        .prefetch_related("items__product", "balance_denominations__denomination")
        .filter(customer__email__icontains=email.strip())
    )
