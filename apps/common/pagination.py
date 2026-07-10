"""Pagination classes shared by API endpoints."""

from __future__ import annotations

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Default page-number pagination for list APIs."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
