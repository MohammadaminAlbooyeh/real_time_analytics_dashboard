from datetime import datetime, timezone
from typing import Any
from backend.processors.base_processor import BaseProcessor


class TumblingWindow(BaseProcessor):
    def __init__(self, name: str = "tumbling_window", window_seconds: int = 300):
        super().__init__(name)
        self.window_seconds = window_seconds
        self.buffer: list[dict] = []

    async def process(self, data: dict) -> dict | None:
        self.buffer.append(data)
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - self.window_seconds
        self.buffer = [d for d in self.buffer if self._get_ts(d) >= cutoff]

        window_start = int(now.timestamp() / self.window_seconds) * self.window_seconds
        window_end = window_start + self.window_seconds

        window_data = [d for d in self.buffer if window_start <= self._get_ts(d) < window_end]
        if not window_data:
            return None

        values = [d["value"] for d in window_data if "value" in d]
        return {
            "window_start": datetime.fromtimestamp(window_start).isoformat(),
            "window_end": datetime.fromtimestamp(window_end).isoformat(),
            "avg": sum(values) / len(values) if values else 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "count": len(values),
        }

    def _get_ts(self, data: dict) -> float:
        ts = data.get("timestamp")
        if isinstance(ts, str):
            return datetime.fromisoformat(ts).timestamp()
        if isinstance(ts, (int, float)):
            return ts
        return datetime.now(timezone.utc).timestamp()
