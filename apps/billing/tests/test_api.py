"""API endpoint tests."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.billing.models import Denomination
from apps.products.models import Product


@pytest.fixture
def api_client() -> APIClient:
    """Return DRF API client.

    Returns:
        API client.
    """
    return APIClient()


@pytest.mark.django_db
def test_product_list_api_returns_products(api_client: APIClient) -> None:
    """Product list API should return active products."""
    Product.objects.create(
        product_id="P001",
        name="Keyboard",
        available_stock=5,
        unit_price=Decimal("100.00"),
        tax_percentage=Decimal("10.00"),
    )

    response = api_client.get(reverse("products:product-list"))

    assert response.status_code == 200
    assert response.json()[0]["product_id"] == "P001"


@pytest.mark.django_db
def test_invoice_create_and_customer_history_api(
    api_client: APIClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invoice API should create invoices and expose customer history."""
    monkeypatch.setattr("apps.billing.services.send_invoice_email_task.delay", lambda invoice_id: None)
    Product.objects.create(
        product_id="P001",
        name="Keyboard",
        available_stock=5,
        unit_price=Decimal("100.00"),
        tax_percentage=Decimal("10.00"),
    )
    Denomination.objects.create(value=10, available_quantity=10)

    response = api_client.post(
        reverse("billing:invoice-list-create"),
        {
            "customer_email": "buyer@example.com",
            "paid_amount": "120.00",
            "items": [{"product_id": "P001", "quantity": 1}],
        },
        format="json",
    )

    assert response.status_code == 201
    history_response = api_client.get(reverse("customers:customer-history", kwargs={"email": "BUYER"}))
    assert history_response.status_code == 200
    assert history_response.json()[0]["customer_email"] == "buyer@example.com"


@pytest.mark.django_db
def test_invoice_detail_api_returns_not_found(api_client: APIClient) -> None:
    """Invoice detail API should return 404 for unknown invoices."""
    response = api_client.get(reverse("billing:invoice-detail", kwargs={"pk": 999}))

    assert response.status_code == 404
