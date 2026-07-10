"""Tests for invoice business service."""

from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from apps.billing.models import BalanceDenomination, Denomination, Invoice
from apps.billing.services import InvoiceService
from apps.products.models import Product


@pytest.fixture
def product() -> Product:
    """Create a stock-backed product.

    Returns:
        Product fixture.
    """
    return Product.objects.create(
        product_id="P001",
        name="Keyboard",
        available_stock=10,
        unit_price=Decimal("100.00"),
        tax_percentage=Decimal("10.00"),
    )


@pytest.fixture
def denominations() -> list[Denomination]:
    """Create denomination inventory.

    Returns:
        Denomination fixtures.
    """
    return [
        Denomination.objects.create(value=100, available_quantity=10),
        Denomination.objects.create(value=10, available_quantity=10),
    ]


@pytest.mark.django_db
def test_create_invoice_deducts_stock_and_creates_balance(
    product: Product,
    denominations: list[Denomination],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invoice creation should persist records and update inventory."""
    monkeypatch.setattr("apps.billing.services.send_invoice_email_task.delay", lambda invoice_id: None)

    invoice = InvoiceService.create_invoice(
        {
            "customer_email": "buyer@example.com",
            "paid_amount": Decimal("250.00"),
            "items": [{"product_id": product.product_id, "quantity": 2}],
            "denominations": [],
        }
    )

    product.refresh_from_db()
    assert invoice.total_amount == Decimal("220.00")
    assert invoice.balance_amount == Decimal("30.00")
    assert product.available_stock == 8
    assert invoice.items.count() == 1
    balance_entry = BalanceDenomination.objects.get(invoice=invoice, denomination__value=10)
    assert balance_entry.quantity_given == 3


@pytest.mark.django_db
def test_create_invoice_uses_rounded_down_total_and_submitted_denominations(
    product: Product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invoice service should calculate balance from rounded-down net price."""
    monkeypatch.setattr("apps.billing.services.send_invoice_email_task.delay", lambda invoice_id: None)
    Denomination.objects.create(value=50, available_quantity=0)
    Denomination.objects.create(value=10, available_quantity=0)
    Denomination.objects.create(value=1, available_quantity=0)
    product.unit_price = Decimal("100.55")
    product.tax_percentage = Decimal("10.00")
    product.save(update_fields=["unit_price", "tax_percentage"])

    invoice = InvoiceService.create_invoice(
        {
            "customer_email": "buyer@example.com",
            "paid_amount": Decimal("200.00"),
            "items": [{"product_id": product.product_id, "quantity": 1}],
            "denominations": [
                {"value": 50, "count": 2},
                {"value": 10, "count": 5},
                {"value": 1, "count": 10},
            ],
        }
    )

    assert invoice.total_amount == Decimal("110.61")
    assert invoice.rounded_total_amount == Decimal("110")
    assert invoice.balance_amount == Decimal("90.00")
    assert Denomination.objects.get(value=50).available_quantity == 1
    assert Denomination.objects.get(value=10).available_quantity == 1


@pytest.mark.django_db
def test_create_invoice_rolls_back_when_stock_is_insufficient(
    product: Product,
    denominations: list[Denomination],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failed invoice creation should not persist partial data."""
    monkeypatch.setattr("apps.billing.services.send_invoice_email_task.delay", lambda invoice_id: None)

    with pytest.raises(ValidationError):
        InvoiceService.create_invoice(
            {
                "customer_email": "buyer@example.com",
                "paid_amount": Decimal("500.00"),
                "items": [{"product_id": product.product_id, "quantity": 50}],
                "denominations": [],
            }
        )

    product.refresh_from_db()
    assert product.available_stock == 10
    assert Invoice.objects.count() == 0
