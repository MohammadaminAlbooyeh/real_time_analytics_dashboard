from datetime import datetime, timedelta, timezone


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def floor_minute(dt: datetime | None = None) -> datetime:
    dt = dt or now_utc()
    return dt.replace(second=0, microsecond=0)


def floor_hour(dt: datetime | None = None) -> datetime:
    dt = dt or now_utc()
    return dt.replace(minute=0, second=0, microsecond=0)


def floor_day(dt: datetime | None = None) -> datetime:
    dt = dt or now_utc()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def range_from_window(window: str) -> timedelta:
    unit = window[-1]
    value = int(window[:-1])
    if unit == "m":
        return timedelta(minutes=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    elif unit == "w":
        return timedelta(weeks=value)
    return timedelta(hours=1)
