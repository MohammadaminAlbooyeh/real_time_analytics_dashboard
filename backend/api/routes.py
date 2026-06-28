from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from backend.api.dependencies import get_db, get_current_user
from backend.api.schemas import (
    MetricCreate, MetricResponse, DataPointRecord,
    DashboardCreate, DashboardItemCreate,
    AlertRuleCreate, AlertEventResponse,
    DataSourceCreate, AnalyticsQuery, CompareQuery,
    UserResponse,
)
from backend.services.metric_service import MetricService
from backend.services.analytics_service import AnalyticsService
from backend.services.dashboard_service import DashboardService
from backend.services.alert_service import AlertService
from backend.services.data_source_service import DataSourceService
from backend.services.export_service import ExportService
from backend.models.user import User
from backend.models.alert import AlertCondition, AlertSeverity, AlertStatus
from backend.models.data_source import DataSourceType

router = APIRouter(prefix="/api/v1", tags=["api"])


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/metrics", response_model=MetricResponse)
async def create_metric(body: MetricCreate, session: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    service = MetricService(session)
    existing = await service.get_by_key(body.key)
    if existing:
        raise HTTPException(status_code=400, detail="Metric key already exists")
    return await service.create_metric(
        name=body.name, key=body.key, description=body.description,
        unit=body.unit, data_type=body.data_type,
        aggregation_method=body.aggregation_method,
    )


@router.get("/metrics", response_model=list[MetricResponse])
async def list_metrics(skip: int = 0, limit: int = 100,
                       session: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    service = MetricService(session)
    return await service.list_metrics(skip=skip, limit=limit)


@router.get("/metrics/{metric_id}", response_model=MetricResponse)
async def get_metric(metric_id: UUID, session: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    service = MetricService(session)
    metric = await service.get_by_id(metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.post("/metrics/{metric_id}/data")
async def record_data(metric_id: UUID, body: DataPointRecord,
                      session: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    service = MetricService(session)
    metric = await service.get_by_id(metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    point = await service.record_value(metric_id, body.value, body.timestamp)
    return {"id": str(point.id), "value": point.value, "timestamp": point.timestamp.isoformat()}


@router.get("/analytics/timeseries")
async def get_timeseries(metric_id: UUID, start: str, end: str, interval: str = "1m",
                         session: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    from datetime import datetime
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    service = AnalyticsService(session)
    return await service.get_timeseries(metric_id, start_dt, end_dt, interval)


@router.get("/analytics/summary/{metric_id}")
async def get_summary(metric_id: UUID, session: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    service = AnalyticsService(session)
    return await service.summary(metric_id)


@router.post("/analytics/compare")
async def compare_periods(body: CompareQuery, session: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    service = AnalyticsService(session)
    return await service.compare_periods(
        body.metric_id, body.current_start, body.current_end,
        body.previous_start, body.previous_end,
    )


@router.post("/dashboards")
async def create_dashboard(body: DashboardCreate,
                           session: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    service = DashboardService(session)
    dashboard = await service.create(
        name=body.name, description=body.description,
        owner_id=current_user.id,
    )
    return {"id": str(dashboard.id), "name": dashboard.name}


@router.get("/dashboards")
async def list_dashboards(session: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    service = DashboardService(session)
    dashboards = await service.list_by_user(current_user.id)
    return [
        {"id": str(d.id), "name": d.name, "description": d.description,
         "item_count": len(d.items), "updated_at": d.updated_at.isoformat()}
        for d in dashboards
    ]


@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: UUID, session: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    service = DashboardService(session)
    dashboard = await service.get_by_id(dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {
        "id": str(dashboard.id),
        "name": dashboard.name,
        "description": dashboard.description,
        "layout": dashboard.layout,
        "items": [
            {
                "id": str(item.id),
                "metric_id": str(item.metric_id),
                "chart_type": item.chart_type,
                "title": item.title,
                "position": {"x": item.position_x, "y": item.position_y},
                "size": {"w": item.width, "h": item.height},
                "config": item.config,
            }
            for item in dashboard.items
        ],
    }


@router.post("/dashboards/{dashboard_id}/items")
async def add_dashboard_item(dashboard_id: UUID, body: DashboardItemCreate,
                             session: AsyncSession = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    service = DashboardService(session)
    item = await service.add_item(
        dashboard_id=dashboard_id, metric_id=body.metric_id,
        chart_type=body.chart_type, title=body.title,
        position_x=body.position_x, position_y=body.position_y,
        width=body.width, height=body.height,
    )
    return {"id": str(item.id)}


@router.delete("/dashboards/items/{item_id}")
async def remove_dashboard_item(item_id: UUID, session: AsyncSession = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    service = DashboardService(session)
    success = await service.remove_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted"}


@router.post("/alerts/rules")
async def create_alert_rule(body: AlertRuleCreate, session: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    service = AlertService(session)
    condition = AlertCondition(body.condition)
    severity = AlertSeverity(body.severity)
    rule = await service.create_rule(
        name=body.name, metric_id=body.metric_id,
        condition=condition, threshold=body.threshold,
        severity=severity, cooldown_minutes=body.cooldown_minutes,
        description=body.description,
    )
    return {"id": str(rule.id), "name": rule.name}


@router.get("/alerts/rules")
async def list_alert_rules(session: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    service = AlertService(session)
    rules = await service.list_rules()
    return [
        {
            "id": str(r.id), "name": r.name, "metric_id": str(r.metric_id),
            "condition": r.condition.value, "threshold": r.threshold,
            "severity": r.severity.value, "enabled": r.enabled,
        }
        for r in rules
    ]


@router.get("/alerts/events", response_model=list[AlertEventResponse])
async def list_alert_events(rule_id: UUID | None = None, status: str | None = None,
                            skip: int = 0, limit: int = 50,
                            session: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    service = AlertService(session)
    alert_status = AlertStatus(status) if status else None
    return await service.list_events(rule_id=rule_id, status=alert_status, skip=skip, limit=limit)


@router.post("/alerts/events/{event_id}/acknowledge")
async def acknowledge_alert(event_id: UUID, session: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    service = AlertService(session)
    event = await service.acknowledge(event_id, current_user.id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"status": "acknowledged"}


@router.post("/alerts/events/{event_id}/resolve")
async def resolve_alert(event_id: UUID, session: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    service = AlertService(session)
    event = await service.resolve(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"status": "resolved"}


@router.post("/datasources")
async def create_data_source(body: DataSourceCreate, session: AsyncSession = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    service = DataSourceService(session)
    ds = await service.create(
        name=body.name, source_type=DataSourceType(body.type),
        config_json=body.config_json,
    )
    return {"id": str(ds.id), "name": ds.name, "type": ds.type.value}


@router.get("/datasources")
async def list_data_sources(session: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    service = DataSourceService(session)
    sources = await service.list_sources()
    return [
        {
            "id": str(s.id), "name": s.name, "type": s.type.value,
            "status": s.status.value, "last_collected_at": s.last_collected_at.isoformat() if s.last_collected_at else None,
        }
        for s in sources
    ]


@router.get("/export/csv")
async def export_csv(metric_id: UUID, start: str, end: str,
                     session: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    from datetime import datetime
    from fastapi.responses import StreamingResponse
    metric_service = MetricService(session)
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    points = await metric_service.get_values(metric_id, start_dt, end_dt)
    data = [
        {"timestamp": p.timestamp.isoformat(), "value": p.value}
        for p in points
    ]
    filename, media_type, content = ExportService.to_csv(data)
    return StreamingResponse(iter([content]), media_type=media_type,
                             headers={"Content-Disposition": f"attachment; filename={filename}"})
