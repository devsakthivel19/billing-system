"""Reusable mixins for views and services."""

from __future__ import annotations

from typing import Any


class SerializerContextMixin:
    """Provide a consistent serializer context for template/API views."""

    def get_serializer_context(self) -> dict[str, Any]:
        """Return serializer context including the current request.

        Returns:
            Serializer context dictionary.
        """
        return {"request": getattr(self, "request", None)}
