from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from config.database_config import async_session_factory
from backend.services.analytics_service import AnalyticsService
from backend.services.export_service import ExportService
from backend.utils.logger import get_logger

logger = get_logger("report_generation")


async def generate_daily_report():
    logger.info("Starting daily report generation")
    async with async_session_factory() as session:
        analytics = AnalyticsService(session)
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=1)
        result = await analytics.get_timeseries(None, start, now)
        return result
