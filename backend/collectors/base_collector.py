from abc import ABC, abstractmethod
from typing import Any
from backend.utils.logger import get_logger


class BaseCollector(ABC):
    def __init__(self, name: str, config: dict | None = None):
        self.name = name
        self.config = config or {}
        self.logger = get_logger(f"collector.{name}")

    @abstractmethod
    async def collect(self) -> list[dict[str, Any]]:
        pass

    async def validate(self, data: list[dict]) -> bool:
        return True

    async def cleanup(self):
        pass
