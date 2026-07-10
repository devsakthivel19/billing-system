"""Root URL configuration for the Billing System project."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/products/", include("apps.products.urls")),
    path("api/customers/", include("apps.customers.urls")),
    path("api/invoices/", include("apps.billing.urls")),
    path("", include("apps.billing.web_urls")),
]
