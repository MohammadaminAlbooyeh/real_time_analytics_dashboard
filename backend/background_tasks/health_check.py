from config.redis_config import get_redis
from config.database_config import async_session_factory
from sqlalchemy import text
from backend.utils.logger import get_logger

logger = get_logger("health_check")


async def health_check():
    results = {"database": False, "redis": False}
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            results["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    try:
        redis = get_redis()
        await redis.ping()
        results["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")

    return results
