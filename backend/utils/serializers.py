import json
from datetime import datetime, date
from uuid import UUID


class AnalyticsJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


def serialize(obj):
    return json.loads(json.dumps(obj, cls=AnalyticsJSONEncoder))
