"""Domain-specific exceptions for billing workflows."""

from __future__ import annotations

from rest_framework.exceptions import APIException, ValidationError


class InvoiceGenerationException(ValidationError):
    """Represent a validation failure while generating an invoice."""


class InsufficientStockException(InvoiceGenerationException):
    """Represent insufficient product stock for an invoice line."""


class InvalidDenominationException(InvoiceGenerationException):
    """Represent invalid or impossible denomination allocation."""


class EmailDeliveryException(APIException):
    """Represent an invoice email delivery failure."""

    status_code = 503
    default_detail = "Invoice email could not be delivered."
    default_code = "email_delivery_failed"
