"""
POST-body pagination helper.

Input: {"page": 1, "pageSize": 10} in the JSON body.
Output: page slice + metadata (page, pageSize, total, totalPages, hasNext,
hasPrev). `page > totalPages` is NOT an error — we return an empty `items[]`
so the client can detect "end of list" via `hasNext == false`.

Edge cases explicitly handled:
    - page / pageSize missing           -> defaults applied
    - page <= 0, pageSize <= 0          -> ValidationError
    - non-integer values                -> ValidationError
    - pageSize > MAX_PAGE_SIZE (100)    -> ValidationError
    - page > last page                  -> empty items, hasNext=false
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


@dataclass
class PaginationResult:
    items: list[Any]
    page: int
    page_size: int
    total: int

    @property
    def total_pages(self) -> int:
        if self.total == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1 and self.total_pages > 0

    def to_dict(self, items_data: list[Any]) -> dict[str, Any]:
        return {
            "items": items_data,
            "page": self.page,
            "page_size": self.page_size,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }


def _parse_positive_int(raw: Any, field: str, default: int, maximum: int | None = None) -> int:
    if raw is None or raw == "":
        return default
    if isinstance(raw, bool) or isinstance(raw, float):
        raise ValidationError({field: [f"{field} must be an integer."]})
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ValidationError({field: [f"{field} must be an integer."]})
    if value < 1:
        raise ValidationError({field: [f"{field} must be >= 1."]})
    if maximum is not None and value > maximum:
        raise ValidationError({field: [f"{field} cannot exceed {maximum}."]})
    return value


def paginate(queryset: QuerySet, data: dict[str, Any]) -> PaginationResult:
    data = data or {}
    page = _parse_positive_int(data.get("page"), "page", DEFAULT_PAGE)
    page_size = _parse_positive_int(
        data.get("page_size") or data.get("pageSize"),
        "pageSize",
        DEFAULT_PAGE_SIZE,
        maximum=MAX_PAGE_SIZE,
    )

    total = queryset.count()
    offset = (page - 1) * page_size
    items = list(queryset[offset : offset + page_size]) if total > 0 else []
    return PaginationResult(items=items, page=page, page_size=page_size, total=total)
