"""
RequestIdMiddleware — assigns / propagates an X-Request-Id for every request.

- Reuses the incoming `X-Request-Id` header when present (useful for tracing
  across services); otherwise generates a dashed UUID4.
- Exposes the ID via `request.request_id`, via the contextvar used by
  response helpers, and via the `X-Request-Id` response header.

Encryption-middleware placement (future)
----------------------------------------
When an EncryptionMiddleware is added (AES/RSA over the JSON body), order
matters. In `MIDDLEWARE`, place it AFTER `RequestIdMiddleware` and BEFORE
any auth/permission layer so DRF's parsers see decrypted bytes:

    MIDDLEWARE = [
        "common.middleware.RequestIdMiddleware",
        "common.middleware.EncryptionMiddleware",    # <— decrypts request here
        "django.middleware.security.SecurityMiddleware",
        ...
    ]

Two Django specifics to remember when implementing that middleware:

1. `request.body` is cached on first access (`HttpRequest._body`). If your
   decryption needs to replace the body, set `request._body = decrypted_bytes`
   BEFORE DRF's parsers run (i.e. before the view executes). Simplest safe
   pattern: decrypt inside `process_request`, rewrite `request._body`, and
   reset `request._stream` so nothing reads the raw ciphertext.

2. Don't call `request.body` / `request.POST` / `request.data` inside the
   middleware before decryption happens — reading them locks the body and
   downstream consumers (DRF) will see the original ciphertext.

On the response side, symmetrically wrap `response.content` in
`process_response` after DRF has rendered the standard envelope.
"""
from __future__ import annotations

from django.utils.deprecation import MiddlewareMixin

from .request_context import generate_request_id, set_request_id

REQUEST_ID_HEADER = "X-Request-Id"


class RequestIdMiddleware(MiddlewareMixin):
    def process_request(self, request):
        incoming = request.META.get("HTTP_X_REQUEST_ID")
        rid = (incoming or "").strip() or generate_request_id()
        request.request_id = rid
        set_request_id(rid)
        return None

    def process_response(self, request, response):
        rid = getattr(request, "request_id", None)
        if rid:
            response[REQUEST_ID_HEADER] = rid
        return response
