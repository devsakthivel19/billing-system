"""Application configuration for products."""

from __future__ import annotations

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """Configure the products application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.products"
    verbose_name = "Products"
