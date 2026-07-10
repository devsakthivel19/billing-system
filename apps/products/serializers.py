"""DRF serializers for product APIs."""

from __future__ import annotations

from rest_framework import serializers

from apps.products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serialize products for read APIs."""

    class Meta:
        """Serializer metadata."""

        model = Product
        fields = (
            "id",
            "product_id",
            "name",
            "available_stock",
            "unit_price",
            "tax_percentage",
            "is_active",
        )
