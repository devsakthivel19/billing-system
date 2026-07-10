"""Repository layer for customer persistence operations."""

from __future__ import annotations

from apps.customers.models import Customer


class CustomerRepository:
    """Persistence operations for customers."""

    @staticmethod
    def get_or_create_by_email(email: str) -> tuple[Customer, bool]:
        """Get or create a customer by email.

        Args:
            email: Customer email address.

        Returns:
            Tuple containing customer and created flag.
        """
        return Customer.objects.get_or_create(email=email.lower())

    @staticmethod
    def get_by_email(email: str) -> Customer | None:
        """Find a customer by email.

        Args:
            email: Customer email address.

        Returns:
            Customer instance when found, otherwise ``None``.
        """
        return Customer.objects.filter(email=email.lower()).first()
