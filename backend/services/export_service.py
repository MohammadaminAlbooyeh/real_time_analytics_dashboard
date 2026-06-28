import csv
import io
import json
from datetime import datetime
from typing import Any


class ExportService:
    @staticmethod
    def to_csv(data: list[dict], filename: str = "export.csv") -> tuple[str, str, bytes]:
        output = io.StringIO()
        if not data:
            return filename, "text/csv", b""
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        content = output.getvalue().encode("utf-8")
        return filename, "text/csv", content

    @staticmethod
    def to_json(data: list[dict], filename: str = "export.json") -> tuple[str, str, bytes]:
        content = json.dumps(data, default=str, indent=2).encode("utf-8")
        return filename, "application/json", content
