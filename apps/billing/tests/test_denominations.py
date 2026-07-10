"""Tests for denomination calculation."""

from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from apps.billing.denomination_service import DenominationService
from apps.billing.models import Denomination


@pytest.mark.django_db
def test_greedy_denominations_respect_available_quantity() -> None:
    """Greedy algorithm should return exact balance using available inventory."""
    denominations = [
        Denomination.objects.create(value=500, available_quantity=2),
        Denomination.objects.create(value=200, available_quantity=3),
        Denomination.objects.create(value=100, available_quantity=0),
        Denomination.objects.create(value=50, available_quantity=1),
        Denomination.objects.create(value=20, available_quantity=5),
        Denomination.objects.create(value=10, available_quantity=10),
        Denomination.objects.create(value=5, available_quantity=5),
        Denomination.objects.create(value=2, available_quantity=20),
        Denomination.objects.create(value=1, available_quantity=100),
    ]

    result = DenominationService.calculate_greedy(Decimal("786"), denominations)

    assert result == {500: 1, 200: 1, 50: 1, 20: 1, 10: 1, 5: 1, 1: 1}


@pytest.mark.django_db
def test_greedy_denominations_raise_when_exact_balance_is_impossible() -> None:
    """Greedy algorithm should fail when exact change cannot be produced."""
    denominations = [Denomination.objects.create(value=5, available_quantity=1)]

    with pytest.raises(ValidationError):
        DenominationService.calculate_greedy(Decimal("3"), denominations)


@pytest.mark.django_db
def test_greedy_denominations_reject_fractional_balance() -> None:
    """Greedy algorithm should reject non-whole balance amounts."""
    denominations = [Denomination.objects.create(value=1, available_quantity=10)]

    with pytest.raises(ValidationError):
        DenominationService.calculate_greedy(Decimal("3.50"), denominations)


@pytest.mark.django_db
def test_greedy_denominations_reject_negative_balance() -> None:
    """Greedy algorithm should reject negative balance amounts."""
    denominations = [Denomination.objects.create(value=1, available_quantity=10)]

    with pytest.raises(ValidationError):
        DenominationService.calculate_greedy(Decimal("-1"), denominations)
