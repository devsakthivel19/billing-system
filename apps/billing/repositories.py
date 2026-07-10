"""Repository layer for billing persistence operations."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from django.db.models import QuerySet

from apps.billing.models import BalanceDenomination, Denomination, Invoice, InvoiceItem
from apps.customers.models import Customer
from apps.products.models import Product


class DenominationRepository:
    """Persistence operations for denominations."""

    @staticmethod
    def list_all() -> QuerySet[Denomination]:
        """Return all denominations.

        Returns:
            QuerySet of denominations ordered by value descending.
        """
        return Denomination.objects.all()

    @staticmethod
    def lock_all() -> QuerySet[Denomination]:
        """Lock denomination rows for cash inventory updates.

        Returns:
            QuerySet of locked denomination rows.
        """
        return Denomination.objects.select_for_update().all()


class InvoiceRepository:
    """Persistence operations for invoices."""

    @staticmethod
    def list_all() -> QuerySet[Invoice]:
        """Return all invoices with related details.

        Returns:
            QuerySet of invoices.
        """
        return (
            Invoice.objects.select_related("customer")
            .prefetch_related("items__product", "balance_denominations__denomination")
            .all()
        )

    @staticmethod
    def get_by_id(invoice_id: int) -> Invoice | None:
        """Find an invoice by ID.

        Args:
            invoice_id: Invoice primary key.

        Returns:
            Invoice instance when found, otherwise ``None``.
        """
        return InvoiceRepository.list_all().filter(id=invoice_id).first()

    @staticmethod
    def create(
        *,
        invoice_number: str,
        customer: Customer,
        subtotal: Decimal,
        tax_amount: Decimal,
        total_amount: Decimal,
        paid_amount: Decimal,
        balance_amount: Decimal,
    ) -> Invoice:
        """Create an invoice record.

        Args:
            invoice_number: Generated invoice number.
            customer: Invoice customer.
            subtotal: Total before tax.
            tax_amount: Total tax.
            total_amount: Grand total.
            paid_amount: Amount paid by customer.
            balance_amount: Balance returned to customer.

        Returns:
            Created invoice instance.
        """
        return Invoice.objects.create(
            invoice_number=invoice_number,
            customer=customer,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            paid_amount=paid_amount,
            balance_amount=balance_amount,
        )

    @staticmethod
    def bulk_create_items(items: Iterable[InvoiceItem]) -> list[InvoiceItem]:
        """Bulk create invoice line items.

        Args:
            items: Invoice item instances.

        Returns:
            Created invoice items.
        """
        return InvoiceItem.objects.bulk_create(list(items))

    @staticmethod
    def bulk_create_balance_denominations(
        entries: Iterable[BalanceDenomination],
    ) -> list[BalanceDenomination]:
        """Bulk create returned balance denomination entries.

        Args:
            entries: Balance denomination instances.

        Returns:
            Created balance denomination entries.
        """
        return BalanceDenomination.objects.bulk_create(list(entries))


def build_invoice_item(
    *,
    invoice: Invoice,
    product: Product,
    quantity: int,
    tax_amount: Decimal,
    total_price: Decimal,
) -> InvoiceItem:
    """Build an unsaved invoice item.

    Args:
        invoice: Parent invoice.
        product: Purchased product.
        quantity: Purchased quantity.
        tax_amount: Line tax amount.
        total_price: Line total amount.

    Returns:
        Unsaved invoice item instance.
    """
    return InvoiceItem(
        invoice=invoice,
        product=product,
        quantity=quantity,
        unit_price=product.unit_price,
        tax_percentage=product.tax_percentage,
        tax_amount=tax_amount,
        total_price=total_price,
    )
