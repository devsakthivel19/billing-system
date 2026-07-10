"""Shared validators for model and serializer fields."""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError


def validate_non_negative_decimal(value: Decimal) -> None:
    """Validate that a decimal value is zero or greater.

    Args:
        value: Decimal value to validate.

    Raises:
        ValidationError: If the value is negative.
    """
    if value < Decimal("0"):
        raise ValidationError("Value must be zero or greater.")


def validate_percentage(value: Decimal) -> None:
    """Validate that a decimal value is between 0 and 100.

    Args:
        value: Decimal percentage to validate.

    Raises:
        ValidationError: If the value is outside the valid range.
    """
    if value < Decimal("0") or value > Decimal("100"):
        raise ValidationError("Percentage must be between 0 and 100.")
