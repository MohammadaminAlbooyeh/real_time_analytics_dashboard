from typing import Any
from backend.collectors.base_collector import BaseCollector
from backend.collectors.api_collector import APICollector
from backend.collectors.database_collector import DatabaseCollector
from backend.collectors.file_collector import FileCollector
from backend.collectors.web_scraper_collector import WebScraperCollector
from backend.utils.logger import get_logger

logger = get_logger("collector_manager")

COLLECTOR_MAP = {
    "api": APICollector,
    "database": DatabaseCollector,
    "file": FileCollector,
    "web_scraper": WebScraperCollector,
}


class CollectorManager:
    def __init__(self):
        self.collectors: dict[str, BaseCollector] = {}

    def register(self, collector_type: str, name: str, config: dict | None = None):
        collector_class = COLLECTOR_MAP.get(collector_type)
        if not collector_class:
            raise ValueError(f"Unknown collector type: {collector_type}")
        self.collectors[name] = collector_class(name, config)
        logger.info(f"Registered collector: {name} ({collector_type})")

    async def run_all(self) -> dict[str, list[dict[str, Any]]]:
        results = {}
        for name, collector in self.collectors.items():
            try:
                data = await collector.collect()
                results[name] = data
                logger.info(f"Collector {name} returned {len(data)} items")
            except Exception as e:
                logger.error(f"Collector {name} failed: {e}")
                results[name] = []
        return results

    async def run_single(self, name: str) -> list[dict[str, Any]]:
        collector = self.collectors.get(name)
        if not collector:
            raise ValueError(f"Collector not found: {name}")
        return await collector.collect()

    def unregister(self, name: str):
        self.collectors.pop(name, None)
        logger.info(f"Unregistered collector: {name}")
