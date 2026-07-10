"""Admin registrations for customers."""

from __future__ import annotations

from django.contrib import admin

from apps.customers.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin configuration for customers."""

    list_display = ("email", "created_at")
    search_fields = ("email",)
    ordering = ("email",)
    readonly_fields = ("created_at",)
