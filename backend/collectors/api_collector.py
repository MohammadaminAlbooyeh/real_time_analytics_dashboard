import httpx
from backend.collectors.base_collector import BaseCollector


class APICollector(BaseCollector):
    def __init__(self, name: str, config: dict | None = None):
        super().__init__(name, config)
        self.url = config.get("url", "")
        self.headers = config.get("headers", {})
        self.timeout = config.get("timeout", 30)

    async def collect(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                results_key = self.config.get("results_key")
                if results_key:
                    return data.get(results_key, [data])
                return [data]
            return []
