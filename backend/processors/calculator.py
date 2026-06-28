from typing import Any
from backend.processors.base_processor import BaseProcessor


class Calculator(BaseProcessor):
    def __init__(self, name: str = "calculator", expression: str | None = None):
        super().__init__(name)
        self.expression = expression

    async def process(self, data: dict) -> dict:
        result = dict(data)
        if "value" in data:
            value = float(data["value"])
            result["computed"] = value * 2
        return result
