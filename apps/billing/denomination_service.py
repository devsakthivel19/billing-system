"""Services for calculating payable balance denominations."""

from __future__ import annotations

from decimal import Decimal

from apps.billing.exceptions import InvalidDenominationException
from apps.billing.models import Denomination


class DenominationService:
    """Calculate and reserve returned balance denominations."""

    @staticmethod
    def calculate_greedy(
        balance_amount: Decimal,
        denominations: list[Denomination],
    ) -> dict[int, int]:
        """Calculate exact change using greedy denomination selection.

        Args:
            balance_amount: Amount that must be returned to the customer.
            denominations: Available denomination rows, ideally locked.

        Returns:
            Mapping of denomination value to quantity returned.

        Raises:
            ValidationError: If exact balance cannot be produced.
        """
        if balance_amount < Decimal("0"):
            raise InvalidDenominationException({"balance_amount": "Balance cannot be negative."})

        remaining = int(balance_amount)
        if Decimal(remaining) != balance_amount:
            raise InvalidDenominationException({"balance_amount": "Balance denominations require whole-number amount."})

        result: dict[int, int] = {}
        for denomination in sorted(denominations, key=lambda item: item.value, reverse=True):
            if remaining <= 0:
                break
            quantity = min(remaining // denomination.value, denomination.available_quantity)
            if quantity > 0:
                result[denomination.value] = quantity
                remaining -= denomination.value * quantity

        if remaining != 0:
            raise InvalidDenominationException(
                {"denominations": "Exact balance cannot be produced with available denominations."}
            )
        return result

    @staticmethod
    def apply_deductions(
        denominations: list[Denomination],
        selected_quantities: dict[int, int],
    ) -> None:
        """Deduct selected denomination quantities from inventory.

        Args:
            denominations: Denomination rows to update.
            selected_quantities: Mapping of denomination value to quantity returned.
        """
        for denomination in denominations:
            quantity = selected_quantities.get(denomination.value, 0)
            if quantity:
                denomination.available_quantity -= quantity
