"""Database models for invoices and denominations."""

from __future__ import annotations

from decimal import Decimal, ROUND_FLOOR

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.constants import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS
from apps.common.constants import PERCENTAGE_DECIMAL_PLACES, PERCENTAGE_MAX_DIGITS
from apps.common.validators import validate_percentage


class Invoice(models.Model):
    """Represent a generated customer invoice."""

    invoice_number = models.CharField(max_length=32, unique=True, db_index=True)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="invoices",
    )
    subtotal = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        validators=[MinValueValidator(0)],
    )
    tax_amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        validators=[MinValueValidator(0)],
    )
    total_amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        validators=[MinValueValidator(0)],
    )
    paid_amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        validators=[MinValueValidator(0)],
    )
    balance_amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model metadata for invoices."""

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["invoice_number"], name="billing_inv_invoice_549473_idx"),
            models.Index(fields=["created_at"], name="billing_inv_created_b8dc82_idx"),
        ]

    def __str__(self) -> str:
        """Return the invoice number.

        Returns:
            Invoice display string.
        """
        return self.invoice_number

    @property
    def rounded_total_amount(self) -> Decimal:
        """Return the cash-settlement total rounded down.

        Returns:
            Rounded-down total amount.
        """
        return self.total_amount.to_integral_value(rounding=ROUND_FLOOR)


class InvoiceItem(models.Model):
    """Represent a product line item inside an invoice."""

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="invoice_items",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        validators=[MinValueValidator(0)],
    )
    tax_percentage = models.DecimalField(
        max_digits=PERCENTAGE_MAX_DIGITS,
        decimal_places=PERCENTAGE_DECIMAL_PLACES,
        validators=[validate_percentage],
    )
    tax_amount = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        validators=[MinValueValidator(0)],
    )
    total_price = models.DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        """Model metadata for invoice items."""

        ordering = ["id"]

    def __str__(self) -> str:
        """Return a readable invoice-item label.

        Returns:
            Invoice item display string.
        """
        return f"{self.invoice.invoice_number} - {self.product.product_id}"


class Denomination(models.Model):
    """Represent cash denomination inventory."""

    value = models.PositiveIntegerField(unique=True, validators=[MinValueValidator(1)])
    available_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        """Model metadata for denominations."""

        ordering = ["-value"]

    def __str__(self) -> str:
        """Return a readable denomination label.

        Returns:
            Denomination display string.
        """
        return f"{self.value} x {self.available_quantity}"


class BalanceDenomination(models.Model):
    """Represent denominations returned as customer balance."""

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="balance_denominations",
    )
    denomination = models.ForeignKey(
        Denomination,
        on_delete=models.PROTECT,
        related_name="balance_returns",
    )
    quantity_given = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        """Model metadata for balance denominations."""

        ordering = ["-denomination__value"]
        constraints = [
            models.UniqueConstraint(
                fields=["invoice", "denomination"],
                name="unique_invoice_balance_denomination",
            )
        ]

    def __str__(self) -> str:
        """Return a readable balance-denomination label.

        Returns:
            Balance denomination display string.
        """
        return f"{self.invoice.invoice_number} - {self.denomination.value}"
