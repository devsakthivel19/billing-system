"""API URL declarations for customers."""

from __future__ import annotations

from django.urls import path

from apps.customers.views import CustomerHistoryAPIView

app_name = "customers"

urlpatterns = [
    path("<str:email>/history/", CustomerHistoryAPIView.as_view(), name="customer-history"),
]
