"""Asynchronous billing tasks."""

from __future__ import annotations

import logging

from celery import shared_task

from apps.billing.email_service import InvoiceEmailService
from apps.billing.exceptions import EmailDeliveryException
from apps.billing.repositories import InvoiceRepository

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(EmailDeliveryException,), retry_backoff=True, max_retries=3)
def send_invoice_email_task(self: object, invoice_id: int) -> None:
    """Send an invoice email asynchronously.

    Args:
        self: Bound Celery task instance.
        invoice_id: Invoice primary key.
    """
    invoice = InvoiceRepository.get_by_id(invoice_id)
    if invoice is None:
        logger.warning("Invoice email skipped because invoice does not exist", extra={"invoice_id": invoice_id})
        return

    try:
        InvoiceEmailService.send_invoice_email(invoice)
    except EmailDeliveryException:
        logger.exception("Invoice email task failed", extra={"invoice_id": invoice_id})
        raise
