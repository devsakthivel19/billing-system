"""Application configuration for customers."""

from __future__ import annotations

from django.apps import AppConfig


class CustomersConfig(AppConfig):
    """Configure the customers application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.customers"
    verbose_name = "Customers"
