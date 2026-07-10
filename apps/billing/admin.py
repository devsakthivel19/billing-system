"""Admin registrations for billing models."""

from __future__ import annotations

from django.contrib import admin

from apps.billing.models import BalanceDenomination, Denomination, Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    """Inline invoice items for invoice admin."""

    model = InvoiceItem
    extra = 0
    readonly_fields = (
        "product",
        "quantity",
        "unit_price",
        "tax_percentage",
        "tax_amount",
        "total_price",
    )
    can_delete = False


class BalanceDenominationInline(admin.TabularInline):
    """Inline returned denominations for invoice admin."""

    model = BalanceDenomination
    extra = 0
    readonly_fields = ("denomination", "quantity_given")
    can_delete = False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for invoices."""

    list_display = (
        "invoice_number",
        "customer",
        "total_amount",
        "paid_amount",
        "balance_amount",
        "created_at",
    )
    search_fields = ("invoice_number", "customer__email")
    list_filter = ("created_at",)
    readonly_fields = (
        "invoice_number",
        "customer",
        "subtotal",
        "tax_amount",
        "total_amount",
        "paid_amount",
        "balance_amount",
        "created_at",
    )
    inlines = [InvoiceItemInline, BalanceDenominationInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """Admin configuration for invoice items."""

    list_display = ("invoice", "product", "quantity", "unit_price", "total_price")
    search_fields = ("invoice__invoice_number", "product__product_id", "product__name")


@admin.register(Denomination)
class DenominationAdmin(admin.ModelAdmin):
    """Admin configuration for denominations."""

    list_display = ("value", "available_quantity")
    ordering = ("-value",)


@admin.register(BalanceDenomination)
class BalanceDenominationAdmin(admin.ModelAdmin):
    """Admin configuration for returned balance denominations."""

    list_display = ("invoice", "denomination", "quantity_given")
    search_fields = ("invoice__invoice_number",)
