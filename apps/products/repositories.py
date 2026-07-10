"""Repository layer for product persistence operations."""

from __future__ import annotations

from collections.abc import Iterable

from django.db.models import QuerySet

from apps.products.models import Product


class ProductRepository:
    """Persistence operations for products."""

    @staticmethod
    def active() -> QuerySet[Product]:
        """Return active products.

        Returns:
            QuerySet containing active products.
        """
        return Product.objects.filter(is_active=True)

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
    def save(product: Product, update_fields: list[str] | None = None) -> Product:
        """Persist a product instance.

        Args:
            product: Product to persist.
            update_fields: Optional list of updated fields.

        Returns:
            Saved product instance.
        """
        product.save(update_fields=update_fields)
        return product
