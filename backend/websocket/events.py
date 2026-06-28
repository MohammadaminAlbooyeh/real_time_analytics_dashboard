from typing import Callable
from backend.utils.logger import get_logger

logger = get_logger("ws_events")


class EventBus:
    def __init__(self):
        self.handlers: dict[str, list[Callable]] = {}

    def on(self, event: str, handler: Callable):
        if event not in self.handlers:
            self.handlers[event] = []
        self.handlers[event].append(handler)
        logger.debug(f"Registered handler for {event}")

    async def emit(self, event: str, *args, **kwargs):
        handlers = self.handlers.get(event, [])
        for handler in handlers:
            try:
                await handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Handler for {event} failed: {e}")


event_bus = EventBus()
