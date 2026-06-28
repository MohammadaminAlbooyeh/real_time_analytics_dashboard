import asyncio
from typing import Any, Callable
from backend.utils.logger import get_logger

logger = get_logger("notification_queue")


class NotificationQueue:
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.handlers: list[Callable] = []
        self._running = False

    def add_handler(self, handler: Callable):
        self.handlers.append(handler)

    async def enqueue(self, notification: dict):
        await self.queue.put(notification)

    async def start(self):
        self._running = True
        while self._running:
            try:
                notification = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                for handler in self.handlers:
                    try:
                        await handler(notification)
                    except Exception as e:
                        logger.error(f"Notification handler failed: {e}")
            except asyncio.TimeoutError:
                continue

    async def stop(self):
        self._running = False


notification_queue = NotificationQueue()
