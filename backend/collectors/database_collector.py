import asyncpg
from backend.collectors.base_collector import BaseCollector


class DatabaseCollector(BaseCollector):
    def __init__(self, name: str, config: dict | None = None):
        super().__init__(name, config)
        self.connection_string = config.get("connection_string", "")
        self.query = config.get("query", "")

    async def collect(self) -> list[dict]:
        conn = await asyncpg.connect(self.connection_string)
        try:
            rows = await conn.fetch(self.query)
            return [dict(row) for row in rows]
        finally:
            await conn.close()
