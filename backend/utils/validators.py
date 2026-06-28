import re


EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
METRIC_KEY_PATTERN = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))


def validate_metric_key(key: str) -> bool:
    return bool(METRIC_KEY_PATTERN.match(key))
