"""Tests for seed data command."""

from __future__ import annotations

import pytest
from django.core.management import call_command

from apps.billing.models import Denomination
from apps.products.models import Product


@pytest.mark.django_db
def test_seed_data_command_is_idempotent() -> None:
    """Seed command should create products and denominations idempotently."""
    call_command("seed_data")
    call_command("seed_data")

    assert Product.objects.filter(product_id="P001").count() == 1
    assert Denomination.objects.filter(value=500).count() == 1
