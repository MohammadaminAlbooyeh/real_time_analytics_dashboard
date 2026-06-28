import asyncio
from typing import Callable
from backend.utils.logger import get_logger

logger = get_logger("collection_scheduler")


class CollectionScheduler:
    def __init__(self):
        self.tasks: dict[str, asyncio.Task] = {}
        self._running = False

    async def start(self):
        self._running = True
        logger.info("Collection scheduler started")

    async def stop(self):
        self._running = False
        for name, task in self.tasks.items():
            task.cancel()
        self.tasks.clear()
        logger.info("Collection scheduler stopped")

    def schedule(self, name: str, interval_seconds: int, callback: Callable):
        async def loop():
            while self._running:
                try:
                    await callback()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Scheduled task {name} error: {e}")
                await asyncio.sleep(interval_seconds)

        self.tasks[name] = asyncio.create_task(loop())
        logger.info(f"Scheduled {name} every {interval_seconds}s")

    def unschedule(self, name: str):
        task = self.tasks.pop(name, None)
        if task:
            task.cancel()
