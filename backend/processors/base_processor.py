from abc import ABC, abstractmethod
from typing import Any
from backend.utils.logger import get_logger


class BaseProcessor(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"processor.{name}")

    @abstractmethod
    async def process(self, data: Any) -> Any:
        pass
