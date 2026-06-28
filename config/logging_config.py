import logging
import json
import sys
from config.settings import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "timestamp": self.formatTime(record),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging():
    formatter = JsonFormatter() if settings.log_format == "json" else logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        logging.getLogger(logger_name).handlers.clear()
        logging.getLogger(logger_name).addHandler(handler)
