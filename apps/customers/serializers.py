"""DRF serializers for customer APIs."""

from __future__ import annotations

from rest_framework import serializers


class CustomerHistoryQuerySerializer(serializers.Serializer):
    """Validate customer purchase-history route parameters."""

    email = serializers.EmailField()
