import httpx
import re
from backend.collectors.base_collector import BaseCollector


class WebScraperCollector(BaseCollector):
    def __init__(self, name: str, config: dict | None = None):
        super().__init__(name, config)
        self.url = config.get("url", "")
        self.pattern = config.get("pattern", "")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AnalyticsCollector/1.0)"
        }

    async def collect(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()
            text = response.text
            if self.pattern:
                matches = re.findall(self.pattern, text)
                return [{"value": m} for m in matches]
            return [{"html_length": len(text)}]
