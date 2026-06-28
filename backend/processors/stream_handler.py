from typing import Any, Callable
from backend.processors.base_processor import BaseProcessor
from backend.utils.logger import get_logger

logger = get_logger("stream_handler")


class StreamHandler:
    def __init__(self):
        self.processors: list[BaseProcessor] = []
        self.outputs: list[Callable] = []

    def add_processor(self, processor: BaseProcessor):
        self.processors.append(processor)
        logger.info(f"Added processor: {processor.name}")

    def add_output(self, output: Callable):
        self.outputs.append(output)

    async def handle(self, data: Any) -> Any:
        result = data
        for processor in self.processors:
            try:
                result = await processor.process(result)
                if result is None:
                    return None
            except Exception as e:
                logger.error(f"Processor {processor.name} failed: {e}")
                return None

        for output in self.outputs:
            try:
                await output(result)
            except Exception as e:
                logger.error(f"Output failed: {e}")

        return result
