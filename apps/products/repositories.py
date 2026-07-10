"""Repository layer for product persistence operations."""

from __future__ import annotations

from collections.abc import Iterable

from django.db.models import QuerySet
from django.utils import timezone

from apps.products.models import Product


class ProductRepository:
    """Persistence operations for products."""

    @staticmethod
    def active() -> QuerySet[Product]:
        """Return active products.

        Returns:
            QuerySet containing active products.
        """
        return Product.objects.only(
            "id",
            "product_id",
            "name",
            "available_stock",
            "unit_price",
            "tax_percentage",
            "is_active",
        ).filter(is_active=True)

    @staticmethod
    def get_active_by_product_id(product_id: str) -> Product | None:
        """Find an active product by public product ID.

        Args:
            product_id: Public product identifier.

        Returns:
            Product instance when found, otherwise ``None``.
        """
        return Product.objects.filter(product_id=product_id, is_active=True).first()

    @staticmethod
    def lock_active_by_product_ids(product_ids: Iterable[str]) -> QuerySet[Product]:
        """Lock active product rows for stock-safe updates.

        Args:
            product_ids: Public product identifiers.

        Returns:
            QuerySet of locked product rows.
        """
        return Product.objects.select_for_update().filter(
            product_id__in=list(product_ids),
            is_active=True,
        )

    @staticmethod
    def bulk_update_stock(products: Iterable[Product]) -> None:
        """Persist stock changes for products.

        Args:
            products: Product instances with updated stock.
        """
        product_list = list(products)
        if not product_list:
            return

        updated_at = timezone.now()
        for product in product_list:
            product.updated_at = updated_at
        Product.objects.bulk_update(product_list, ["available_stock", "updated_at"])
