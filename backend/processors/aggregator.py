from datetime import datetime, timezone
from typing import Any
from backend.processors.base_processor import BaseProcessor


class Aggregator(BaseProcessor):
    def __init__(self, name: str = "aggregator", window_seconds: int = 60):
        super().__init__(name)
        self.window_seconds = window_seconds
        self.buffer: list[dict] = []

    async def process(self, data: dict) -> dict | None:
        self.buffer.append(data)
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - self.window_seconds
        self.buffer = [d for d in self.buffer if self._get_ts(d) >= cutoff]

        if len(self.buffer) < 2:
            return None

        values = [d["value"] for d in self.buffer if "value" in d]
        if not values:
            return None

        return {
            "metric_key": data.get("metric_key", "unknown"),
            "window_start": datetime.fromtimestamp(min(self._get_ts(d) for d in self.buffer)).isoformat(),
            "window_end": datetime.fromtimestamp(max(self._get_ts(d) for d in self.buffer)).isoformat(),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "count": len(values),
            "sum": sum(values),
        }

    def _get_ts(self, data: dict) -> float:
        ts = data.get("timestamp")
        if isinstance(ts, str):
            return datetime.fromisoformat(ts).timestamp()
        if isinstance(ts, (int, float)):
            return ts
        return datetime.now(timezone.utc).timestamp()
