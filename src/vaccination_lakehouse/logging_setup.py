"""Logging configuration: JSON lines for jobs, readable text for the terminal.

Every record carries the ``run_id`` of the current process, so all log lines (and, later,
rows in ``ops.run_log``) of one pipeline run can be correlated.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

#: Identifier of this process's run, shared by all log records.
RUN_ID = uuid.uuid4().hex[:12]

# Attributes every LogRecord has; anything else was passed through ``extra=``.
_STANDARD_ATTRS = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime", "run_id"}

# Chatty third-party loggers (py4j talks to the JVM on every Spark call).
_NOISY_LOGGERS = ("py4j", "py4j.clientserver", "urllib3")


class _RunIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.run_id = RUN_ID
        return True


class JsonFormatter(logging.Formatter):
    """One JSON object per line: easy to grep, parse and ship to a log platform."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "run_id": getattr(record, "run_id", RUN_ID),
            "msg": record.getMessage(),
        }
        payload.update({k: v for k, v in record.__dict__.items() if k not in _STANDARD_ATTRS})
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


def configure_logging(level: str = "INFO", json_format: bool = True) -> None:
    """Configure the root logger once; safe to call again (replaces the handler)."""
    handler = logging.StreamHandler()
    handler.addFilter(_RunIdFilter())
    if json_format:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-7s %(name)s [%(run_id)s] %(message)s")
        )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
