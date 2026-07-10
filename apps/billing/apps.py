"""Application configuration for billing."""

from __future__ import annotations

from django.apps import AppConfig


class BillingConfig(AppConfig):
    """Configure the billing application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.billing"
    verbose_name = "Billing"
