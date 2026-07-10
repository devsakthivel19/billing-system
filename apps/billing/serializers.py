"""DRF serializers for invoice APIs."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from rest_framework import serializers

from apps.billing.models import BalanceDenomination, Denomination, Invoice, InvoiceItem


class InvoiceCreateItemSerializer(serializers.Serializer):
    """Validate invoice product line input."""

    product_id = serializers.CharField(max_length=64)
    quantity = serializers.IntegerField(min_value=1)


class PaymentDenominationSerializer(serializers.Serializer):
    """Validate denominations received from customer."""

    value = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=0)


class InvoiceCreateSerializer(serializers.Serializer):
    """Validate invoice creation payload."""

    customer_email = serializers.EmailField(
        error_messages={
            "invalid": "Enter a valid customer email address.",
            "blank": "Customer email is required.",
            "required": "Customer email is required.",
        }
    )
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.00"))
    items = InvoiceCreateItemSerializer(many=True, allow_empty=False)
    denominations = PaymentDenominationSerializer(many=True, required=False, default=list)

    def validate_items(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Validate invoice line uniqueness.

        Args:
            items: Invoice line dictionaries.

        Returns:
            Validated invoice lines.

        Raises:
            serializers.ValidationError: If duplicate product IDs exist.
        """
        product_ids = [item["product_id"] for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Duplicate product IDs are not allowed.")
        return items

    def validate_denominations(self, denominations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Validate received denomination uniqueness.

        Args:
            denominations: Payment denomination dictionaries.

        Returns:
            Validated denominations.

        Raises:
            serializers.ValidationError: If duplicate denominations exist.
        """
        values = [item["value"] for item in denominations]
        if len(values) != len(set(values)):
            raise serializers.ValidationError("Duplicate denominations are not allowed.")
        return denominations


class DenominationSerializer(serializers.ModelSerializer):
    """Serialize denomination inventory."""

    class Meta:
        """Serializer metadata."""

        model = Denomination
        fields = ("id", "value", "available_quantity")


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serialize invoice line items."""

    product_id = serializers.CharField(source="product.product_id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        """Serializer metadata."""

        model = InvoiceItem
        fields = (
            "id",
            "product_id",
            "product_name",
            "quantity",
            "unit_price",
            "tax_percentage",
            "tax_amount",
            "total_price",
        )


class BalanceDenominationSerializer(serializers.ModelSerializer):
    """Serialize returned balance denominations."""

    value = serializers.IntegerField(source="denomination.value", read_only=True)

    class Meta:
        """Serializer metadata."""

        model = BalanceDenomination
        fields = ("value", "quantity_given")


class InvoiceSerializer(serializers.ModelSerializer):
    """Serialize invoice details."""

    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    balance_denominations = BalanceDenominationSerializer(many=True, read_only=True)
    rounded_total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        """Serializer metadata."""

        model = Invoice
        fields = (
            "id",
            "invoice_number",
            "customer_email",
            "subtotal",
            "tax_amount",
            "total_amount",
            "rounded_total_amount",
            "paid_amount",
            "balance_amount",
            "created_at",
            "items",
            "balance_denominations",
        )
