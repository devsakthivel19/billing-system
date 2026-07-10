"""Database models for products."""

from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.constants import (
    MONEY_DECIMAL_PLACES,
    MONEY_MAX_DIGITS,
    PERCENTAGE_DECIMAL_PLACES,
    PERCENTAGE_MAX_DIGITS,
)
from apps.common.validators import validate_percentage


class Product(models.Model):
    """Represent a sellable product and its current stock."""

    product_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    available_stock = models.PositiveIntegerField(default=0)
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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata for products."""

        ordering = ["name"]
        indexes = [
            models.Index(fields=["product_id"], name="products_pr_product_3fdb84_idx"),
            models.Index(fields=["is_active", "name"], name="products_pr_is_acti_3ba8d5_idx"),
        ]

    def __str__(self) -> str:
        """Return a readable product label.

        Returns:
            Product display string.
        """
        return f"{self.product_id} - {self.name}"
