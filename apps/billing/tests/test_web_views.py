"""Tests for template-backed web views."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from apps.billing.models import Invoice
from apps.customers.models import Customer


@pytest.fixture
def client() -> Client:
    """Return Django test client.

    Returns:
        Django test client.
    """
    return Client()


@pytest.mark.django_db
def test_billing_page_renders(client: Client) -> None:
    """Billing page should render successfully."""
    response = client.get(reverse("billing_web:billing-page"))

    assert response.status_code == 200
    assert b"Generate Bill" in response.content


@pytest.mark.django_db
def test_invoice_page_renders(client: Client) -> None:
    """Invoice page should render invoice details."""
    customer = Customer.objects.create(email="buyer@example.com")
    invoice = Invoice.objects.create(
        invoice_number="INV-WEB",
        customer=customer,
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("10.00"),
        total_amount=Decimal("110.00"),
        paid_amount=Decimal("120.00"),
        balance_amount=Decimal("10.00"),
    )

    response = client.get(reverse("billing_web:invoice-page", kwargs={"pk": invoice.id}))

    assert response.status_code == 200
    assert b"INV-WEB" in response.content


@pytest.mark.django_db
def test_purchase_history_page_renders_results(client: Client) -> None:
    """Purchase history page should render matching invoices."""
    customer = Customer.objects.create(email="buyer@example.com")
    Invoice.objects.create(
        invoice_number="INV-HISTORY",
        customer=customer,
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("10.00"),
        total_amount=Decimal("110.00"),
        paid_amount=Decimal("120.00"),
        balance_amount=Decimal("10.00"),
    )

    response = client.get(reverse("billing_web:purchase-history-page"), {"email": "BUYER"})

    assert response.status_code == 200
    assert b"INV-HISTORY" in response.content
