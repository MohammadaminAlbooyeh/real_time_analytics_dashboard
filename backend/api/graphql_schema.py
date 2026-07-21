import strawberry
from typing import List, Optional
from uuid import UUID
from datetime import datetime


@strawberry.type
class MetricType:
    id: strawberry.ID
    name: str
    key: str
    description: Optional[str] = None
    unit: Optional[str] = None
    data_type: str
    is_active: bool
    created_at: str


@strawberry.type
class DataPointType:
    id: strawberry.ID
    metric_id: str
    value: float
    timestamp: str


@strawberry.type
class AnalyticsSummaryType:
    avg_last_24h: Optional[float] = None
    avg_last_7d: Optional[float] = None
    datapoints_last_24h: int = 0


@strawberry.type
class AnomalyType:
    timestamp: str
    value: float
    anomaly_score: float
    severity: str


@strawberry.type
class ForecastPointType:
    timestamp: str
    predicted_value: float
    confidence_lower: float
    confidence_upper: float


@strawberry.type
class AlertRuleType:
    id: strawberry.ID
    name: str
    metric_id: str
    condition: str
    threshold: float
    severity: str
    enabled: bool


@strawberry.type
class Query:
    @strawberry.field
    async def metrics(self, info: strawberry.Info, skip: int = 0, limit: int = 100) -> List[MetricType]:
        from backend.services.metric_service import MetricService
        session = info.context["db"]
        service = MetricService(session)
        metrics = await service.list_metrics(skip=skip, limit=limit)
        return [
            MetricType(
                id=str(m.id), name=m.name, key=m.key,
                description=m.description, unit=m.unit,
                data_type=m.data_type, is_active=m.is_active,
                created_at=m.created_at.isoformat(),
            )
            for m in metrics
        ]

    @strawberry.field
    async def metric(self, info: strawberry.Info, metric_id: str) -> Optional[MetricType]:
        from backend.services.metric_service import MetricService
        session = info.context["db"]
        service = MetricService(session)
        m = await service.get_by_id(UUID(metric_id))
        if not m:
            return None
        return MetricType(
            id=str(m.id), name=m.name, key=m.key,
            description=m.description, unit=m.unit,
            data_type=m.data_type, is_active=m.is_active,
            created_at=m.created_at.isoformat(),
        )

    @strawberry.field
    async def timeseries(
        self, info: strawberry.Info, metric_id: str, start: str, end: str, interval: str = "1m",
    ) -> List[DataPointType]:
        from backend.services.metric_service import MetricService
        session = info.context["db"]
        service = MetricService(session)
        points = await service.get_values(
            UUID(metric_id),
            datetime.fromisoformat(start),
            datetime.fromisoformat(end),
        )
        return [
            DataPointType(
                id=str(p.id), metric_id=str(p.metric_id),
                value=p.value, timestamp=p.timestamp.isoformat(),
            )
            for p in points
        ]

    @strawberry.field
    async def analytics_summary(self, info: strawberry.Info, metric_id: str) -> Optional[AnalyticsSummaryType]:
        from backend.services.analytics_service import AnalyticsService
        session = info.context["db"]
        service = AnalyticsService(session)
        try:
            summary = await service.summary(UUID(metric_id))
            return AnalyticsSummaryType(**summary)
        except ValueError:
            return None

    @strawberry.field
    async def anomalies(
        self, info: strawberry.Info, metric_id: str, lookback_hours: int = 168,
    ) -> List[AnomalyType]:
        from backend.services.ml_service import MLService
        session = info.context["db"]
        service = MLService(session)
        anomalies = await service.detect_anomalies_isolation_forest(
            UUID(metric_id), lookback_hours=lookback_hours,
        )
        return [
            AnomalyType(**a) for a in anomalies
        ]

    @strawberry.field
    async def forecasts(
        self, info: strawberry.Info, metric_id: str, forecast_hours: int = 24,
    ) -> List[ForecastPointType]:
        from backend.services.ml_service import MLService
        session = info.context["db"]
        service = MLService(session)
        forecasts = await service.forecast_values(
            UUID(metric_id), forecast_hours=forecast_hours,
        )
        return [
            ForecastPointType(**f) for f in forecasts
        ]

    @strawberry.field
    async def alert_rules(self, info: strawberry.Info, skip: int = 0, limit: int = 100) -> List[AlertRuleType]:
        from backend.services.alert_service import AlertService
        session = info.context["db"]
        service = AlertService(session)
        rules = await service.list_rules(skip=skip, limit=limit)
        return [
            AlertRuleType(
                id=str(r.id), name=r.name, metric_id=str(r.metric_id),
                condition=r.condition.value, threshold=r.threshold,
                severity=r.severity.value, enabled=r.enabled,
            )
            for r in rules
        ]


schema = strawberry.Schema(query=Query)
