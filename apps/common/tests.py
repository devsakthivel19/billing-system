"""Tests for common utilities and validators."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.common.exceptions import custom_exception_handler
from apps.common.validators import validate_non_negative_decimal, validate_percentage


def test_validate_percentage_rejects_out_of_range_values() -> None:
    """Percentage validator should reject values above 100."""
    with pytest.raises(ValidationError):
        validate_percentage(Decimal("101"))


def test_validate_non_negative_decimal_rejects_negative_values() -> None:
    """Non-negative validator should reject negative decimals."""
    with pytest.raises(ValidationError):
        validate_non_negative_decimal(Decimal("-1"))


def test_custom_exception_handler_formats_validation_errors() -> None:
    """Custom exception handler should normalize DRF validation errors."""
    response = custom_exception_handler(DRFValidationError({"field": "Invalid."}), {})

    assert response is not None
    assert response.status_code == 400
    assert response.data["code"] == "validation_error"


def test_custom_exception_handler_formats_unhandled_errors() -> None:
    """Custom exception handler should return a safe 500 response."""
    response = custom_exception_handler(RuntimeError("boom"), {})

    assert response is not None
    assert response.status_code == 500
    assert response.data["code"] == "internal_server_error"
