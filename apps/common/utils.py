"""Shared utility functions for the Billing System project."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def quantize_money(value: Decimal) -> Decimal:
    """Round a monetary decimal to two places.

    Args:
        value: Decimal amount.

    Returns:
        Amount rounded using financial half-up rounding.
    """
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
