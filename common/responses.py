"""
Standard API response envelope.

All API responses follow the same shape:

Success:
    {"result": "success", "data": <dict | list | None>, "message": str}

Error:
    {"result": "error",   "data": {"errors": <dict | None>}, "message": str}

Use `success_response` / `error_response` from views, and let the custom
exception handler (common.exceptions.custom_exception_handler) wrap errors
raised by DRF/Django automatically.
"""
from __future__ import annotations

from typing import Any

from rest_framework import status as http_status
from rest_framework.response import Response

from . import error_codes as codes
from .request_context import get_request_id

RESULT_SUCCESS = "success"
RESULT_ERROR = "error"


def _envelope(base: dict) -> dict:
    rid = get_request_id()
    if rid:
        base["request_id"] = rid
    return base


def success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = http_status.HTTP_200_OK,
) -> Response:
    return Response(
        _envelope({"result": RESULT_SUCCESS, "data": data, "message": message}),
        status=status_code,
    )


def error_response(
    message: str = "Something went wrong",
    errors: Any = None,
    code: str = codes.REQUEST_FAILED,
    status_code: int = http_status.HTTP_400_BAD_REQUEST,
) -> Response:
    """`errors` is a dict of {field: [messages]} or None for non-validation errors.

    `code` must be one of the constants in `common.error_codes` so frontend
    clients can branch on it reliably.
    """
    return Response(
        _envelope(
            {
                "result": RESULT_ERROR,
                "code": code,
                "data": {"errors": errors},
                "message": message,
            }
        ),
        status=status_code,
    )
