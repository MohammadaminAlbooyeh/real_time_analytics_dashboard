import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.metric import Metric
from backend.models.time_series import TimeSeriesDataPoint
from backend.utils.logger import get_logger

logger = get_logger("metric_service")


class MetricService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_metric(self, name: str, key: str, description: str | None = None,
                            unit: str | None = None, data_type: str = "float",
                            aggregation_method: str = "avg") -> Metric:
        metric = Metric(
            name=name, key=key, description=description,
            unit=unit, data_type=data_type, aggregation_method=aggregation_method,
        )
        self.session.add(metric)
        await self.session.flush()
        logger.info(f"Created metric {metric.id} key={key}")
        return metric

    async def get_by_id(self, metric_id: uuid.UUID) -> Metric | None:
        result = await self.session.execute(select(Metric).where(Metric.id == metric_id))
        return result.scalar_one_or_none()

    async def get_by_key(self, key: str) -> Metric | None:
        result = await self.session.execute(select(Metric).where(Metric.key == key))
        return result.scalar_one_or_none()

    async def list_metrics(self, skip: int = 0, limit: int = 100) -> list[Metric]:
        result = await self.session.execute(
            select(Metric).offset(skip).limit(limit).order_by(Metric.created_at.desc())
        )
        return list(result.scalars().all())

    async def record_value(self, metric_id: uuid.UUID, value: float, timestamp=None) -> TimeSeriesDataPoint:
        from datetime import datetime, timezone
        point = TimeSeriesDataPoint(
            metric_id=metric_id,
            value=value,
            timestamp=timestamp or datetime.now(timezone.utc),
        )
        self.session.add(point)
        await self.session.flush()
        return point

    async def get_values(self, metric_id: uuid.UUID, start, end, limit: int = 1000) -> list[TimeSeriesDataPoint]:
        result = await self.session.execute(
            select(TimeSeriesDataPoint)
            .where(TimeSeriesDataPoint.metric_id == metric_id)
            .where(TimeSeriesDataPoint.timestamp >= start)
            .where(TimeSeriesDataPoint.timestamp <= end)
            .order_by(TimeSeriesDataPoint.timestamp.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_aggregate(self, metric_id: uuid.UUID, start, end, agg: str = "avg") -> float | None:
        agg_func = getattr(func, agg)
        result = await self.session.execute(
            select(agg_func(TimeSeriesDataPoint.value))
            .where(TimeSeriesDataPoint.metric_id == metric_id)
            .where(TimeSeriesDataPoint.timestamp >= start)
            .where(TimeSeriesDataPoint.timestamp <= end)
        )
        return result.scalar()
