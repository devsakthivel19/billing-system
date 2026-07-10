"""API and template views for billing."""

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.selectors import get_invoice, list_denominations, list_invoices
from apps.billing.serializers import InvoiceCreateSerializer, InvoiceSerializer
from apps.billing.services import InvoiceService
from apps.products.selectors import list_active_products


class InvoiceListCreateAPIView(APIView):
    """Expose invoice list and invoice creation API endpoint."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return invoice list.

        Args:
            request: Incoming API request.
            *args: Positional route arguments.
            **kwargs: Keyword route arguments.

        Returns:
            API response for invoice listing.
        """
        serializer = InvoiceSerializer(list_invoices(), many=True)
        return Response(serializer.data)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a new invoice.

        Args:
            request: Incoming API request.
            *args: Positional route arguments.
            **kwargs: Keyword route arguments.

        Returns:
            API response for invoice creation.
        """
        serializer = InvoiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = InvoiceService.create_invoice(serializer.validated_data)
        return Response(InvoiceSerializer(invoice).data, status=201)


class InvoiceDetailAPIView(APIView):
    """Expose invoice detail API endpoint."""

    def get(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        """Return invoice detail by primary key.

        Args:
            request: Incoming API request.
            pk: Invoice primary key captured from the route.
            *args: Positional route arguments.
            **kwargs: Keyword route arguments.

        Returns:
            API response for invoice detail.
        """
        invoice = InvoiceService.get_invoice_or_raise(pk)
        return Response(InvoiceSerializer(invoice).data)


class BillingPageView(View):
    """Render the billing entry page."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Return the billing page.

        Args:
            request: Incoming HTTP request.
            *args: Positional route arguments.
            **kwargs: Keyword route arguments.

        Returns:
            HTTP response for the billing page.
        """
        return render(
            request,
            "billing/billing_page.html",
            {
                "products": list_active_products(),
                "denominations": list_denominations(),
            },
        )


class InvoicePageView(View):
    """Render a generated invoice page."""

    def get(self, request: HttpRequest, pk: int, *args: Any, **kwargs: Any) -> HttpResponse:
        """Return the invoice display page.

        Args:
            request: Incoming HTTP request.
            pk: Invoice primary key captured from the route.
            *args: Positional route arguments.
            **kwargs: Keyword route arguments.

        Returns:
            HTTP response for the invoice page.
        """
        invoice = get_invoice(pk)
        if invoice is None:
            messages.error(request, "Invoice not found.")
            return redirect("billing_web:billing-page")
        return render(request, "billing/invoice_page.html", {"invoice": invoice})


class PurchaseHistoryPageView(View):
    """Render the purchase history page."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Return the purchase history page.

        Args:
            request: Incoming HTTP request.
            *args: Positional route arguments.
            **kwargs: Keyword route arguments.

        Returns:
            HTTP response for the purchase history page.
        """
        email = request.GET.get("email", "")
        invoices = []
        if email:
            from apps.customers.selectors import get_customer_invoices

            invoices = get_customer_invoices(email)
        return render(
            request,
            "billing/purchase_history.html",
            {
                "email": email,
                "invoices": invoices,
            },
        )
