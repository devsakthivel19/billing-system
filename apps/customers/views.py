"""API views for customers."""

from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.serializers import InvoiceSerializer
from apps.customers.selectors import get_customer_invoices


class CustomerHistoryAPIView(APIView):
    """Expose purchase history for a customer email address."""

    def get(self, request: Request, email: str, *args: Any, **kwargs: Any) -> Response:
        """Return invoices purchased by a customer.

        Args:
            request: Incoming API request.
            email: Customer email captured from the route.
            *args: Positional route arguments.
            **kwargs: Keyword route arguments.

        Returns:
            API response for the customer history endpoint.
        """
        invoices = get_customer_invoices(email)
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
