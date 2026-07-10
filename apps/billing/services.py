"""Service layer for invoice business operations."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR
from typing import Any
from uuid import uuid4

from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from apps.billing.denomination_service import DenominationService
from apps.billing.models import BalanceDenomination, Denomination, Invoice
from apps.billing.repositories import (
    DenominationRepository,
    InvoiceRepository,
    build_invoice_item,
)
from apps.billing.tasks import send_invoice_email_task
from apps.common.utils import quantize_money
from apps.customers.repositories import CustomerRepository
from apps.products.models import Product
from apps.products.repositories import ProductRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class InvoiceLineCalculation:
    """Calculated amount details for one invoice line."""

    product: Product
    quantity: int
    subtotal: Decimal
    tax_amount: Decimal
    total_price: Decimal


class InvoiceService:
    """Business service for invoice generation."""

    @staticmethod
    def get_invoice_or_raise(invoice_id: int) -> Invoice:
        """Return an invoice or raise a 404 exception.

        Args:
            invoice_id: Invoice primary key.

        Returns:
            Invoice instance.

        Raises:
            NotFound: If invoice does not exist.
        """
        invoice = InvoiceRepository.get_by_id(invoice_id)
        if invoice is None:
            raise NotFound("Invoice not found.")
        return invoice

    @staticmethod
    def create_invoice(validated_data: dict[str, Any]) -> Invoice:
        """Create an invoice inside an atomic transaction.

        Args:
            validated_data: Validated invoice payload.

        Returns:
            Created invoice instance.

        Raises:
            ValidationError: If business validation fails.
        """
        with transaction.atomic():
            customer_email = validated_data["customer_email"].lower()
            paid_amount = validated_data["paid_amount"]
            item_payloads = validated_data["items"]

            product_ids = [item["product_id"] for item in item_payloads]
            products = list(ProductRepository.lock_active_by_product_ids(product_ids))
            product_map = {product.product_id: product for product in products}

            missing = sorted(set(product_ids) - set(product_map))
            if missing:
                raise ValidationError({"items": f"Products not found: {', '.join(missing)}"})

            line_calculations = InvoiceService._calculate_lines(item_payloads, product_map)
            subtotal = quantize_money(sum((line.subtotal for line in line_calculations), Decimal("0.00")))
            tax_amount = quantize_money(sum((line.tax_amount for line in line_calculations), Decimal("0.00")))
            total_amount = quantize_money(subtotal + tax_amount)
            rounded_total_amount = InvoiceService._round_down_for_cash(total_amount)

            if paid_amount < rounded_total_amount:
                raise ValidationError(
                    {
                        "paid_amount": (
                            "Insufficient cash paid. Paid amount must be at least "
                            f"{rounded_total_amount}."
                        )
                    }
                )

            balance_amount = quantize_money(paid_amount - rounded_total_amount)
            denominations = list(DenominationRepository.lock_all())
            InvoiceService._apply_submitted_denomination_counts(
                denominations,
                validated_data.get("denominations", []),
            )
            returned_denominations = DenominationService.calculate_greedy(balance_amount, denominations)

            customer, _created = CustomerRepository.get_or_create_by_email(customer_email)
            invoice = InvoiceRepository.create(
                invoice_number=InvoiceService._generate_invoice_number(),
                customer=customer,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                paid_amount=paid_amount,
                balance_amount=balance_amount,
            )

            InvoiceRepository.bulk_create_items(
                build_invoice_item(
                    invoice=invoice,
                    product=line.product,
                    quantity=line.quantity,
                    tax_amount=line.tax_amount,
                    total_price=line.total_price,
                )
                for line in line_calculations
            )
            InvoiceService._deduct_stock(line_calculations)
            DenominationService.apply_deductions(denominations, returned_denominations)
            InvoiceRepository.bulk_create_balance_denominations(
                BalanceDenomination(
                    invoice=invoice,
                    denomination=InvoiceService._find_denomination(denominations, value),
                    quantity_given=quantity,
                )
                for value, quantity in returned_denominations.items()
            )

            transaction.on_commit(lambda: send_invoice_email_task.delay(invoice.id))
            logger.info("Invoice generated", extra={"invoice_id": invoice.id})
            return InvoiceRepository.get_by_id(invoice.id) or invoice

    @staticmethod
    def _calculate_lines(
        item_payloads: list[dict[str, Any]],
        product_map: dict[str, Product],
    ) -> list[InvoiceLineCalculation]:
        """Calculate invoice line amounts and validate stock.

        Args:
            item_payloads: Validated item payloads.
            product_map: Mapping of product ID to locked product.

        Returns:
            Calculated invoice lines.

        Raises:
            ValidationError: If stock is insufficient.
        """
        lines: list[InvoiceLineCalculation] = []
        for item in item_payloads:
            product = product_map[item["product_id"]]
            quantity = item["quantity"]
            if product.available_stock < quantity:
                raise ValidationError(
                    {
                        "items": (
                            f"Insufficient stock for {product.product_id} ({product.name}). "
                            f"Requested {quantity}, but only {product.available_stock} available."
                        )
                    }
                )
            line_subtotal = quantize_money(product.unit_price * quantity)
            line_tax = quantize_money(line_subtotal * product.tax_percentage / Decimal("100"))
            lines.append(
                InvoiceLineCalculation(
                    product=product,
                    quantity=quantity,
                    subtotal=line_subtotal,
                    tax_amount=line_tax,
                    total_price=quantize_money(line_subtotal + line_tax),
                )
            )
        return lines

    @staticmethod
    def _deduct_stock(lines: list[InvoiceLineCalculation]) -> None:
        """Deduct product stock for calculated lines.

        Args:
            lines: Calculated invoice lines.
        """
        for line in lines:
            line.product.available_stock -= line.quantity
            line.product.save(update_fields=["available_stock", "updated_at"])

    @staticmethod
    def _apply_submitted_denomination_counts(
        denominations: list[Denomination],
        submitted_denominations: list[dict[str, Any]],
    ) -> None:
        """Use page-submitted cash counts as current shop denomination availability.

        Args:
            denominations: Locked denomination rows.
            submitted_denominations: Denomination count payload from the billing page.

        Raises:
            ValidationError: If the payload references an unknown denomination.
        """
        if not submitted_denominations:
            return

        denomination_map = {denomination.value: denomination for denomination in denominations}
        unknown_values = sorted(
            item["value"] for item in submitted_denominations if item["value"] not in denomination_map
        )
        if unknown_values:
            raise ValidationError(
                {"denominations": f"Unknown denominations: {', '.join(map(str, unknown_values))}"}
            )

        for item in submitted_denominations:
            denomination = denomination_map[item["value"]]
            denomination.available_quantity = item["count"]
            denomination.save(update_fields=["available_quantity"])

    @staticmethod
    def _round_down_for_cash(total_amount: Decimal) -> Decimal:
        """Round net price down for cash settlement.

        Args:
            total_amount: Exact invoice total.

        Returns:
            Whole-number rounded-down amount.
        """
        return total_amount.to_integral_value(rounding=ROUND_FLOOR)

    @staticmethod
    def _find_denomination(denominations: list[Denomination], value: int) -> Denomination:
        """Find a denomination object by value.

        Args:
            denominations: Denomination instances.
            value: Denomination value to find.

        Returns:
            Matching denomination instance.

        Raises:
            ValidationError: If denomination value is missing.
        """
        for denomination in denominations:
            if denomination.value == value:
                return denomination
        raise ValidationError({"denominations": f"Denomination {value} is not configured."})

    @staticmethod
    def _generate_invoice_number() -> str:
        """Generate a unique invoice number.

        Returns:
            Invoice number string.
        """
        return f"INV-{uuid4().hex[:12].upper()}"
