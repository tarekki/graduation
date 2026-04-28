"""
Custom DRF exception handler producing the standard envelope.

Envelope:
    {
        "result": "error",
        "code": "<MACHINE_CODE>",          # stable, frontend switches on this
        "data":  {"errors": {field: [msgs]} | None},
        "message": "<human-readable>",
        "requestId": "...",
    }

Wire up in settings:
    REST_FRAMEWORK = {"EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler"}
"""
from __future__ import annotations

from typing import Any

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf_exc
from rest_framework.response import Response
from rest_framework.views import exception_handler

from . import error_codes as codes
from .request_context import get_request_id
from .responses import RESULT_ERROR


def _flatten_errors(detail: Any) -> Any:
    """Turn DRF error detail into a {field: [messages]} dict (or None).

    - dict: each value becomes list[str].
    - list/scalar: returned under "nonFieldErrors" so the shape is always consistent.
    """
    if detail is None:
        return None

    if isinstance(detail, dict):
        out: dict[str, list[str]] = {}
        for key, value in detail.items():
            out[str(key)] = _messages_to_list(value)
        return out

    return {"nonFieldErrors": _messages_to_list(detail)}


def _messages_to_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, dict):
        flat: list[str] = []
        for sub in value.values():
            flat.extend(_messages_to_list(sub))
        return flat
    return [str(value)]


def _top_message(errors: dict | None, default: str) -> str:
    """Pick a human message from the first error, falling back to `default`."""
    if not errors:
        return default
    first_key, first_val = next(iter(errors.items()))
    first_msg = first_val[0] if isinstance(first_val, list) and first_val else str(first_val)
    if first_key in ("nonFieldErrors", "detail"):
        return first_msg
    return f"{first_key}: {first_msg}"


def _classify(exc) -> tuple[str, str]:
    """Return (error_code, default_message) for a DRF/Django exception."""
    if isinstance(exc, drf_exc.ValidationError):
        return codes.VALIDATION_ERROR, "Validation error"
    if isinstance(exc, drf_exc.NotAuthenticated):
        return codes.NOT_AUTHENTICATED, "Authentication required"
    if isinstance(exc, drf_exc.AuthenticationFailed):
        return codes.AUTHENTICATION_FAILED, "Authentication failed"
    if isinstance(exc, drf_exc.PermissionDenied):
        return codes.PERMISSION_DENIED, "You do not have permission to perform this action"
    if isinstance(exc, drf_exc.NotFound):
        return codes.NOT_FOUND, "Resource not found"
    if isinstance(exc, drf_exc.MethodNotAllowed):
        return codes.METHOD_NOT_ALLOWED, "Method not allowed"
    if isinstance(exc, drf_exc.Throttled):
        return codes.THROTTLED, "Too many requests"
    if isinstance(exc, drf_exc.ParseError):
        return codes.PARSE_ERROR, "Malformed request body"
    if isinstance(exc, drf_exc.UnsupportedMediaType):
        return codes.UNSUPPORTED_MEDIA_TYPE, "Unsupported media type"
    return codes.REQUEST_FAILED, "Request failed"


def custom_exception_handler(exc, context) -> Response | None:
    if isinstance(exc, Http404):
        exc = drf_exc.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = drf_exc.PermissionDenied()

    response = exception_handler(exc, context)
    if response is None:
        return None

    error_code, default_msg = _classify(exc)

    if isinstance(exc, drf_exc.ValidationError):
        errors = _flatten_errors(exc.detail)
        message = _top_message(errors, default_msg)
    else:
        errors = None
        detail = getattr(exc, "detail", None)
        message = str(detail) if detail else default_msg

    payload: dict = {
        "result": RESULT_ERROR,
        "code": error_code,
        "data": {"errors": errors},
        "message": message,
    }
    rid = get_request_id()
    if rid:
        payload["request_id"] = rid
    response.data = payload
    return response
