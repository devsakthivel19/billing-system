"""API URL declarations for products."""

from __future__ import annotations

from django.urls import path

from apps.products.views import ProductListAPIView

app_name = "products"

urlpatterns = [
    path("", ProductListAPIView.as_view(), name="product-list"),
]
