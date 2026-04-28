"""
Per-request correlation ID.

A contextvar lets response helpers and the exception handler look up the
current request's ID without having to plumb it through every call site.
"""
from __future__ import annotations

import contextvars
import uuid

_request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


def generate_request_id() -> str:
    """Dashed UUID4 (36 chars) — readable in logs/Postman/Kibana."""
    return str(uuid.uuid4())


def set_request_id(value: str | None) -> None:
    _request_id_var.set(value)


def get_request_id() -> str | None:
    return _request_id_var.get()
