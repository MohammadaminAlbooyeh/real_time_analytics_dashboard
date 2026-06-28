from typing import Any
from backend.processors.base_processor import BaseProcessor


class Transformer(BaseProcessor):
    def __init__(self, name: str = "transformer", mappings: dict | None = None):
        super().__init__(name)
        self.mappings = mappings or {}

    async def process(self, data: dict) -> dict:
        if not self.mappings:
            return data
        result = {}
        for target_key, source_key in self.mappings.items():
            keys = source_key.split(".")
            value = data
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    value = None
                    break
            result[target_key] = value
        return result
