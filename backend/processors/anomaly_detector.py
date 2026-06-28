import statistics
from typing import Any
from backend.processors.base_processor import BaseProcessor


class AnomalyDetector(BaseProcessor):
    def __init__(self, name: str = "anomaly_detector", window_size: int = 20, threshold: float = 2.0):
        super().__init__(name)
        self.window_size = window_size
        self.threshold = threshold
        self.history: list[float] = []

    async def process(self, data: dict) -> dict:
        result = dict(data)
        value = data.get("value")
        if value is None:
            return result

        self.history.append(float(value))
        if len(self.history) > self.window_size:
            self.history.pop(0)

        if len(self.history) >= 5:
            mean = statistics.mean(self.history)
            stdev = statistics.stdev(self.history) if len(self.history) > 1 else 0
            if stdev > 0:
                z_score = (float(value) - mean) / stdev
                result["is_anomaly"] = abs(z_score) > self.threshold
                result["z_score"] = round(z_score, 4)
            else:
                result["is_anomaly"] = False
                result["z_score"] = 0.0
        else:
            result["is_anomaly"] = False
            result["z_score"] = 0.0

        return result
