"""Read/query helpers for customers."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.billing.models import Invoice
from apps.billing.repositories import InvoiceRepository


def get_customer_invoices(email: str) -> QuerySet[Invoice]:
    """Return invoices for customer emails matching search text.

    Args:
        email: Customer email search text.

    Returns:
        QuerySet of invoices for matching customers.
    """
    return InvoiceRepository.list_by_customer_email(email)
