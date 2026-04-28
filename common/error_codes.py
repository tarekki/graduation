"""
Stable machine-readable error codes used in the response envelope.

Keep this file as the single source of truth. Frontend clients can branch on
`code` (never on `message`, which is human-readable and may be localized).
"""
from __future__ import annotations

VALIDATION_ERROR = "VALIDATION_ERROR"
NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
PERMISSION_DENIED = "PERMISSION_DENIED"
NOT_FOUND = "NOT_FOUND"
METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
THROTTLED = "THROTTLED"
PARSE_ERROR = "PARSE_ERROR"
UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"
REQUEST_FAILED = "REQUEST_FAILED"
INTERNAL_ERROR = "INTERNAL_ERROR"
