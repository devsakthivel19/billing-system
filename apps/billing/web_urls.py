"""Template URL declarations for billing pages."""

from __future__ import annotations

from django.urls import path

from apps.billing.views import BillingPageView, InvoicePageView, PurchaseHistoryPageView

app_name = "billing_web"

urlpatterns = [
    path("", BillingPageView.as_view(), name="billing-page"),
    path("invoices/<int:pk>/", InvoicePageView.as_view(), name="invoice-page"),
    path("history/", PurchaseHistoryPageView.as_view(), name="purchase-history-page"),
]
