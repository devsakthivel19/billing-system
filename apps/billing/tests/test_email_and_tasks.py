"""Tests for invoice email service and Celery task."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core import mail
from django.test import override_settings

from apps.billing.email_service import InvoiceEmailService
from apps.billing.exceptions import EmailDeliveryException
from apps.billing.models import Invoice
from apps.billing.tasks import send_invoice_email_task
from apps.customers.models import Customer


@pytest.fixture
def invoice() -> Invoice:
    """Create an invoice for email tests.

    Returns:
        Invoice fixture.
    """
    customer = Customer.objects.create(email="buyer@example.com")
    return Invoice.objects.create(
        invoice_number="INV-TEST",
        customer=customer,
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("10.00"),
        total_amount=Decimal("110.00"),
        paid_amount=Decimal("120.00"),
        balance_amount=Decimal("10.00"),
    )


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_invoice_email_service_sends_message(invoice: Invoice) -> None:
    """Email service should send a rendered invoice email."""
    InvoiceEmailService.send_invoice_email(invoice)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["buyer@example.com"]


@pytest.mark.django_db
def test_invoice_email_service_raises_domain_exception_on_delivery_failure(
    invoice: Invoice,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Email service should expose delivery failures as domain exceptions."""

    def raise_delivery_error(*args: object, **kwargs: object) -> None:
        """Raise a fake mail-provider failure."""
        raise RuntimeError("SMTP unavailable")

    monkeypatch.setattr("django.core.mail.EmailMultiAlternatives.send", raise_delivery_error)

    with pytest.raises(EmailDeliveryException):
        InvoiceEmailService.send_invoice_email(invoice)


@pytest.mark.django_db
def test_send_invoice_email_task_calls_service(
    invoice: Invoice,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Celery task should load invoice and delegate to email service."""
    called = []
    monkeypatch.setattr(
        "apps.billing.tasks.InvoiceEmailService.send_invoice_email",
        lambda loaded_invoice: called.append(loaded_invoice.id),
    )

    send_invoice_email_task(invoice.id)

    assert called == [invoice.id]
