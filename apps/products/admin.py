"""Admin registrations for products."""

from __future__ import annotations

from django.contrib import admin

from apps.products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for products."""

    list_display = (
        "product_id",
        "name",
        "available_stock",
        "unit_price",
        "tax_percentage",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("product_id", "name")
    ordering = ("name",)
