"""Invoice rendering helpers."""

from __future__ import annotations

from django.template.loader import render_to_string

from apps.billing.models import Invoice


class InvoiceRenderService:
    """Render invoice content for notifications."""

    @staticmethod
    def render_email_html(invoice: Invoice) -> str:
        """Render HTML invoice email content.

        Args:
            invoice: Invoice to render.

        Returns:
            Rendered HTML email body.
        """
        return render_to_string("billing/email_invoice.html", {"invoice": invoice})
