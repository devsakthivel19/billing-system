"""API views for products."""

from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.selectors import list_active_products
from apps.products.serializers import ProductSerializer


class ProductListAPIView(APIView):
    """Expose product list API endpoint."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return the product list.

        Args:
            request: Incoming API request.
            *args: Positional route arguments.
            **kwargs: Keyword route arguments.

        Returns:
            API response for the product list endpoint.
        """
        serializer = ProductSerializer(list_active_products(), many=True)
        return Response(serializer.data)
