"""Database models for customers."""

from __future__ import annotations

from django.db import models


class Customer(models.Model):
    """Represent a customer identified by email address."""

    email = models.EmailField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model metadata for customers."""

        ordering = ["email"]
        indexes = [models.Index(fields=["email"], name="customers_c_email_f3b102_idx")]

    def __str__(self) -> str:
        """Return the customer email.

        Returns:
            Customer display string.
        """
        return self.email
