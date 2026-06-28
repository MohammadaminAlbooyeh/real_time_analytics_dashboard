from datetime import datetime, timezone, timedelta
from sqlalchemy import delete
from config.database_config import async_session_factory
from backend.models.time_series import TimeSeriesDataPoint
from backend.utils.logger import get_logger

logger = get_logger("cleanup_tasks")


async def cleanup_old_data(retention_days: int = 90):
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    logger.info(f"Cleaning up data older than {cutoff.isoformat()}")
    async with async_session_factory() as session:
        result = await session.execute(
            delete(TimeSeriesDataPoint).where(TimeSeriesDataPoint.timestamp < cutoff)
        )
        await session.commit()
        logger.info(f"Cleaned up {result.rowcount} old data points")
