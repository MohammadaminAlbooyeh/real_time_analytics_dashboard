import logging

logger = logging.getLogger("analytics")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"analytics.{name}")
