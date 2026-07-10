"""Email helpers for invoice notifications."""

from __future__ import annotations

import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from apps.billing.exceptions import EmailDeliveryException
from apps.billing.invoice_service import InvoiceRenderService
from apps.billing.models import Invoice

logger = logging.getLogger(__name__)


class InvoiceEmailService:
    """Send invoice emails."""

    @staticmethod
    def send_invoice_email(invoice: Invoice) -> None:
        """Send an invoice email to the customer.

        Args:
            invoice: Invoice instance to email.
        """
        html_body = InvoiceRenderService.render_email_html(invoice)
        message = EmailMultiAlternatives(
            subject=f"Invoice {invoice.invoice_number}",
            body=f"Invoice {invoice.invoice_number} total: {invoice.total_amount}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.customer.email],
        )
        message.attach_alternative(html_body, "text/html")
        try:
            message.send(fail_silently=False)
        except (OSError, SMTPException) as exc:
            logger.exception("Invoice email delivery failed", extra={"invoice_id": invoice.id})
            raise EmailDeliveryException() from exc
        logger.info("Invoice email sent", extra={"invoice_id": invoice.id})
