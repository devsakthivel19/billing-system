"""Seed products and denominations for local development."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand

from apps.billing.models import Denomination
from apps.products.models import Product


class Command(BaseCommand):
    """Insert deterministic development seed data."""

    help = "Seed products and denominations for the billing system."

    def handle(self, *args: Any, **options: Any) -> None:
        """Create or update default products and denomination inventory.

        Args:
            *args: Positional command arguments.
            **options: Command options.
        """
        products = [
            ("P001", "Keyboard", 100, Decimal("750.00"), Decimal("18.00")),
            ("P002", "Mouse", 150, Decimal("450.00"), Decimal("18.00")),
            ("P003", "USB Cable", 200, Decimal("120.00"), Decimal("5.00")),
            ("P004", "Notebook", 250, Decimal("60.00"), Decimal("0.00")),
        ]
        denominations = [500, 200, 100, 50, 20, 10, 5, 2, 1]

        for product_id, name, stock, price, tax in products:
            Product.objects.update_or_create(
                product_id=product_id,
                defaults={
                    "name": name,
                    "available_stock": stock,
                    "unit_price": price,
                    "tax_percentage": tax,
                    "is_active": True,
                },
            )

        for value in denominations:
            Denomination.objects.update_or_create(
                value=value,
                defaults={"available_quantity": 100},
            )

        self.stdout.write(self.style.SUCCESS("Seed data inserted successfully."))
