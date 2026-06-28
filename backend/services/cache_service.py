from typing import Any
import json
from config.redis_config import get_redis
from backend.utils.logger import get_logger

logger = get_logger("cache_service")


class CacheService:
    def __init__(self):
        self.redis = get_redis()

    async def get(self, key: str) -> Any | None:
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        serialized = json.dumps(value, default=str)
        await self.redis.setex(key, ttl, serialized)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key)

    async def invalidate_pattern(self, pattern: str) -> None:
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break
