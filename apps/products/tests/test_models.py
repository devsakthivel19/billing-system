"""Product model tests."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.products.models import Product
from apps.products.repositories import ProductRepository


@pytest.mark.django_db
def test_product_string_representation() -> None:
    """Product string representation should include ID and name."""
    product = Product.objects.create(
        product_id="P001",
        name="Keyboard",
        available_stock=10,
        unit_price=Decimal("100.00"),
        tax_percentage=Decimal("10.00"),
    )

    assert str(product) == "P001 - Keyboard"


@pytest.mark.django_db
def test_product_repository_finds_active_product() -> None:
    """Product repository should find active products by product ID."""
    product = Product.objects.create(
        product_id="P001",
        name="Keyboard",
        available_stock=10,
        unit_price=Decimal("100.00"),
        tax_percentage=Decimal("10.00"),
    )

    assert ProductRepository.get_active_by_product_id("P001") == product
    assert ProductRepository.get_active_by_product_id("UNKNOWN") is None
