"""Asynchronous billing tasks."""

from __future__ import annotations

import logging

from celery import shared_task

from apps.billing.email_service import InvoiceEmailService
from apps.billing.models import Invoice

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_invoice_email_task(self: object, invoice_id: int) -> None:
    """Send an invoice email asynchronously.

    Args:
        self: Bound Celery task instance.
        invoice_id: Invoice primary key.
    """
    try:
        invoice = Invoice.objects.select_related("customer").prefetch_related(
            "items__product",
            "balance_denominations__denomination",
        ).get(id=invoice_id)
        InvoiceEmailService.send_invoice_email(invoice)
    except Invoice.DoesNotExist:
        logger.warning("Invoice email skipped because invoice does not exist", extra={"invoice_id": invoice_id})
    except Exception:
        logger.exception("Invoice email task failed", extra={"invoice_id": invoice_id})
        raise
