"""API URL declarations for billing."""

from __future__ import annotations

from django.urls import path

from apps.billing.views import InvoiceDetailAPIView, InvoiceListCreateAPIView

app_name = "billing"

urlpatterns = [
    path("", InvoiceListCreateAPIView.as_view(), name="invoice-list-create"),
    path("<int:pk>/", InvoiceDetailAPIView.as_view(), name="invoice-detail"),
]
