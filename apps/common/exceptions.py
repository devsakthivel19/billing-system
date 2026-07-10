"""Custom exception helpers for API error responses."""

from __future__ import annotations

import logging
from typing import Any

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class ConflictError(APIException):
    """Represent a request conflict that should return HTTP 409."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "The request conflicts with the current resource state."
    default_code = "conflict"


class ServiceUnavailableError(APIException):
    """Represent an unavailable downstream service."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "The requested service is temporarily unavailable."
    default_code = "service_unavailable"


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Normalize DRF exception responses.

    Args:
        exc: Raised exception instance.
        context: DRF exception context.

    Returns:
        A DRF response when the exception is handled, otherwise ``None``.
    """
    response = exception_handler(exc, context)

    if response is None:
        logger.exception("Unhandled API exception", exc_info=exc)
        return Response(
            {
                "detail": "Internal server error.",
                "code": "internal_server_error",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = getattr(exc, "default_code", "error")
    if isinstance(exc, Http404):
        code = "not_found"
    if isinstance(exc, ValidationError):
        code = "validation_error"

    response.data = {
        "detail": response.data,
        "code": str(code),
    }
    return response
