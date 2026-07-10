"""Read/query helpers for billing data."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.billing.models import Denomination, Invoice
from apps.billing.repositories import DenominationRepository, InvoiceRepository


def list_invoices() -> QuerySet[Invoice]:
    """Return invoices for API listing.

    Returns:
        QuerySet of invoices.
    """
    return InvoiceRepository.list_all()


def get_invoice(invoice_id: int) -> Invoice | None:
    """Return an invoice by ID.

    Args:
        invoice_id: Invoice primary key.

    Returns:
        Invoice instance when found, otherwise ``None``.
    """
    return InvoiceRepository.get_by_id(invoice_id)


def list_denominations() -> QuerySet[Denomination]:
    """Return all denomination inventory rows.

    Returns:
        QuerySet of denominations.
    """
    return DenominationRepository.list_all()
