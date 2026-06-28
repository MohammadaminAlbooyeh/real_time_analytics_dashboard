import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.time_series import TimeSeriesDataPoint
from backend.models.metric import Metric
from backend.utils.logger import get_logger

logger = get_logger("analytics_service")


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_timeseries(self, metric_id: uuid.UUID, start: datetime, end: datetime,
                             interval: str = "1m") -> list[dict]:
        bucket = self._interval_to_trunc(interval)
        rows = await self.session.execute(
            select(
                func.date_trunc(bucket, TimeSeriesDataPoint.timestamp).label("bucket"),
                func.avg(TimeSeriesDataPoint.value).label("avg"),
                func.max(TimeSeriesDataPoint.value).label("max"),
                func.min(TimeSeriesDataPoint.value).label("min"),
                func.count(TimeSeriesDataPoint.value).label("count"),
            )
            .where(TimeSeriesDataPoint.metric_id == metric_id)
            .where(TimeSeriesDataPoint.timestamp >= start)
            .where(TimeSeriesDataPoint.timestamp <= end)
            .group_by(func.date_trunc(bucket, TimeSeriesDataPoint.timestamp))
            .order_by("bucket")
        )
        return [
            {
                "timestamp": r.bucket.isoformat(),
                "avg": round(float(r.avg), 4) if r.avg else None,
                "max": round(float(r.max), 4) if r.max else None,
                "min": round(float(r.min), 4) if r.min else None,
                "count": r.count,
            }
            for r in rows
        ]

    async def compare_periods(self, metric_id: uuid.UUID, current_start: datetime,
                              current_end: datetime, previous_start: datetime,
                              previous_end: datetime) -> dict:
        current = await self.get_timeseries(metric_id, current_start, current_end)
        previous = await self.get_timeseries(metric_id, previous_start, previous_end)
        current_avg = sum(p["avg"] for p in current if p["avg"]) / len(current) if current else 0
        previous_avg = sum(p["avg"] for p in previous if p["avg"]) / len(previous) if previous else 0
        change_pct = ((current_avg - previous_avg) / previous_avg * 100) if previous_avg else 0
        return {
            "current_avg": round(current_avg, 4),
            "previous_avg": round(previous_avg, 4),
            "change_pct": round(change_pct, 2),
            "current_period": current,
            "previous_period": previous,
        }

    async def summary(self, metric_id: uuid.UUID) -> dict:
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(weeks=1)
        result = await self.session.execute(
            select(
                func.avg(TimeSeriesDataPoint.value).filter(
                    TimeSeriesDataPoint.timestamp >= day_ago
                ).label("avg_1d"),
                func.avg(TimeSeriesDataPoint.value).filter(
                    TimeSeriesDataPoint.timestamp >= week_ago
                ).label("avg_7d"),
                func.count(TimeSeriesDataPoint.value).filter(
                    TimeSeriesDataPoint.timestamp >= day_ago
                ).label("count_1d"),
            )
            .where(TimeSeriesDataPoint.metric_id == metric_id)
        )
        r = result.one()
        return {
            "avg_last_24h": round(float(r.avg_1d), 4) if r.avg_1d else None,
            "avg_last_7d": round(float(r.avg_7d), 4) if r.avg_7d else None,
            "datapoints_last_24h": r.count_1d or 0,
        }

    def _interval_to_trunc(self, interval: str) -> str:
        mapping = {"1m": "minute", "5m": "minute", "15m": "minute",
                    "1h": "hour", "1d": "day", "1w": "week"}
        return mapping.get(interval, "minute")
