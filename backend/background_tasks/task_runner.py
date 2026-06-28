import asyncio
from typing import Callable
from backend.utils.logger import get_logger

logger = get_logger("task_runner")


class TaskRunner:
    def __init__(self):
        self.tasks: dict[str, asyncio.Task] = {}
        self._running = False

    async def start(self):
        self._running = True
        logger.info("Task runner started")

    async def stop(self):
        self._running = False
        for name, task in self.tasks.items():
            task.cancel()
        self.tasks.clear()
        logger.info("Task runner stopped")

    def add_task(self, name: str, callback: Callable, interval_seconds: int):
        async def loop():
            await asyncio.sleep(interval_seconds)
            while self._running:
                try:
                    await callback()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Task {name} failed: {e}")
                await asyncio.sleep(interval_seconds)

        self.tasks[name] = asyncio.create_task(loop())
        logger.info(f"Added background task: {name} (every {interval_seconds}s)")

    def remove_task(self, name: str):
        task = self.tasks.pop(name, None)
        if task:
            task.cancel()
