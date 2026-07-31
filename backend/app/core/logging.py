"""
Logging configuration — structured, rotated, context-aware.

Architecture:
    - ContextFilter injects request_id and user_id from contextvars
      into every LogRecord automatically. No explicit passing needed.
    - Development: human-readable single-line format to console.
    - Production: JSON lines to console + files for log aggregators.
    - Two rotating log files: app.log (INFO+) and error.log (ERROR+).
    - Called once at startup from main.py before any other logging.

Design decisions:
    - Uses stdlib logging, not third-party (structlog, loguru). Zero
      extra dependencies, works with uvicorn's logging, and every
      Python developer already knows the API.
    - JSON formatting is hand-built (not json.dumps per field) to keep
      it fast — logging is on the hot path of every request.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.context import request_id_var, user_id_var


# ---------------------------------------------------------------------------
# Context Filter — injects request_id and user_id into all log records
# ---------------------------------------------------------------------------

class ContextFilter(logging.Filter):
    """
    Logging filter that pulls request_id and user_id from contextvars
    and attaches them to every LogRecord.

    Applied to the root logger so ALL loggers in the app (including
    third-party libraries) automatically carry request context.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.user_id = user_id_var.get()
        return True


# ---------------------------------------------------------------------------
# JSON Formatter — structured logs for production
# ---------------------------------------------------------------------------

class JSONFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON objects.

    Output is optimized for log aggregators (ELK, CloudWatch, Datadog).
    Each line is a valid JSON object — no multiline, no parsing needed.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "request_id": getattr(record, "request_id", "-"),
            "user_id": getattr(record, "user_id", "-"),
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include exception info if present
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


# ---------------------------------------------------------------------------
# Setup Function
# ---------------------------------------------------------------------------

LOG_DIR = Path("logs")

# Human-readable format for development console output
DEV_FORMAT = (
    "%(asctime)s | %(levelname)-8s | [%(request_id)s] "
    "| %(name)s | %(message)s"
)

DEV_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(*, log_level: str = "INFO", json_logs: bool = False) -> None:
    """
    Configure the application logging system.

    Called once at startup, before any other code runs. Configures:
        - Root logger level
        - Console handler (human-readable or JSON) with context filter
        - File handlers with rotation (production only) with context filter

    The ContextFilter is attached to each HANDLER (not the root logger)
    so it runs for ALL log records regardless of which logger emitted them.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_logs: If True, use JSON format for console and file output.
                   Automatically True in production via config.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # Remove any existing handlers (prevents duplicate logs on reload)
    root_logger.handlers.clear()

    context_filter = ContextFilter()

    # --- Console Handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level.upper())
    console_handler.addFilter(context_filter)

    if json_logs:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(fmt=DEV_FORMAT, datefmt=DEV_DATE_FORMAT)
        )

    root_logger.addHandler(console_handler)

    # --- File Handlers (only when JSON logs are enabled, i.e., production) ---
    if json_logs:
        LOG_DIR.mkdir(exist_ok=True)

        # app.log — all logs at INFO+
        app_file_handler = RotatingFileHandler(
            LOG_DIR / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        app_file_handler.setLevel(logging.INFO)
        app_file_handler.setFormatter(JSONFormatter())
        app_file_handler.addFilter(context_filter)
        root_logger.addHandler(app_file_handler)

        # error.log — errors only at ERROR+
        error_file_handler = RotatingFileHandler(
            LOG_DIR / "error.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(JSONFormatter())
        error_file_handler.addFilter(context_filter)
        root_logger.addHandler(error_file_handler)

    # --- Quiet noisy third-party loggers ---
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging configured — level=%s, json=%s", log_level, json_logs
    )
