"""Tests for billing serializers."""

from __future__ import annotations

from apps.billing.serializers import InvoiceCreateSerializer


def test_invoice_serializer_rejects_duplicate_products() -> None:
    """Invoice serializer should reject duplicate product IDs."""
    serializer = InvoiceCreateSerializer(
        data={
            "customer_email": "buyer@example.com",
            "paid_amount": "100.00",
            "items": [
                {"product_id": "P001", "quantity": 1},
                {"product_id": "P001", "quantity": 2},
            ],
        }
    )

    assert serializer.is_valid() is False
    assert "items" in serializer.errors


def test_invoice_serializer_rejects_invalid_customer_email() -> None:
    """Invoice serializer should reject invalid customer email addresses."""
    serializer = InvoiceCreateSerializer(
        data={
            "customer_email": "buyer",
            "paid_amount": "100.00",
            "items": [{"product_id": "P001", "quantity": 1}],
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["customer_email"][0] == "Enter a valid customer email address."
