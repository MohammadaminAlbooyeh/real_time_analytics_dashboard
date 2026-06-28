import csv
import json
import io
import aiofiles
from backend.collectors.base_collector import BaseCollector


class FileCollector(BaseCollector):
    def __init__(self, name: str, config: dict | None = None):
        super().__init__(name, config)
        self.file_path = config.get("file_path", "")
        self.file_type = config.get("file_type", "csv")

    async def collect(self) -> list[dict]:
        async with aiofiles.open(self.file_path, mode="r") as f:
            content = await f.read()

        if self.file_type == "json":
            return json.loads(content) if isinstance(json.loads(content), list) else [json.loads(content)]
        elif self.file_type == "csv":
            reader = csv.DictReader(io.StringIO(content))
            return list(reader)
        return []
