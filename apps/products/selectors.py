"""Read/query helpers for products."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.products.models import Product
from apps.products.repositories import ProductRepository


def list_active_products() -> QuerySet[Product]:
    """Return active products for list views and APIs.

    Returns:
        QuerySet of active products.
    """
    return ProductRepository.active()
