"""
Logging helpers.

- `RequestIdFilter` attaches the current request's ID (from the contextvar) to
  every LogRecord as `record.request_id`. Wire it up in the `LOGGING` setting
  so any logger — including Django's, DRF's, and project loggers — emits
  correlation IDs without callers passing `extra={...}` manually.

- `JsonFormatter` emits one-line JSON per log record (for Kibana/Loki/CloudWatch).
  Toggled by `LOG_FORMAT=json` (standard, human-readable text otherwise).
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from .request_context import get_request_id


class RequestIdFilter(logging.Filter):
    NO_REQUEST = "-"

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or self.NO_REQUEST
        return True


class JsonFormatter(logging.Formatter):
    """One-line JSON log records, stable key order, ISO-8601 UTC timestamps."""

    RESERVED = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message", "asctime", "request_id",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "requestId": getattr(record, "request_id", RequestIdFilter.NO_REQUEST),
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key in self.RESERVED or key.startswith("_"):
                continue
            try:
                json.dumps(value)
                payload[key] = value
            except (TypeError, ValueError):
                payload[key] = repr(value)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)
