from backend.websocket.manager import manager
from backend.utils.logger import get_logger

logger = get_logger("broadcasters")


async def broadcast_metric_update(metric_key: str, value: float, timestamp: str):
    await manager.broadcast({
        "type": "metric_update",
        "metric_key": metric_key,
        "value": value,
        "timestamp": timestamp,
    })


async def broadcast_alert(alert_data: dict):
    await manager.broadcast({
        "type": "alert",
        **alert_data,
    })


async def broadcast_dashboard_update(dashboard_id: str):
    await manager.broadcast({
        "type": "dashboard_update",
        "dashboard_id": dashboard_id,
    })
