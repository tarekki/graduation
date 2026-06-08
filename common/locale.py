"""
Request locale resolution for localized API output.

Clients select a language with a request header — either a custom `Locale`
header or the standard `Accept-Language` — e.g.:

    Locale: ar
    Accept-Language: ar-SY,ar;q=0.9,en;q=0.8

Only the leading 2-letter language subtag is considered. Unknown or missing
values fall back to ``DEFAULT_LOCALE`` (English).
"""
from __future__ import annotations

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("en", "ar")


def get_locale(request, *, default: str = DEFAULT_LOCALE) -> str:
    """Return a supported 2-letter locale code ('en' | 'ar') for the request.

    Precedence: custom `Locale` header → `Accept-Language` → ``default``.
    """
    if request is None:
        return default

    raw = request.headers.get("Locale") or request.headers.get("Accept-Language") or ""
    token = raw.split(",")[0].split(";")[0].strip().lower()
    code = token[:2]
    return code if code in SUPPORTED_LOCALES else default
