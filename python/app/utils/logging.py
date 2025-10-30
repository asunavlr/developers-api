import json
import logging
import time
from typing import Any, Dict


def configure_logging() -> None:
    logger = logging.getLogger("app")
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            payload: Dict[str, Any] = {
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
                "time": int(time.time() * 1000),
            }
            # Include extra fields if present
            for key in ("method", "path", "status", "latency_ms", "request_id", "user_id"):
                if hasattr(record, key):
                    payload[key] = getattr(record, key)
            return json.dumps(payload, ensure_ascii=False)

    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)


def get_logger() -> logging.Logger:
    return logging.getLogger("app")