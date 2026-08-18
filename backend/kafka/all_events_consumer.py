"""Consumer for smart-ecommerce-platform events feeding analytics metrics."""

import json
from datetime import datetime
from typing import Any

from aiokafka import AIOKafkaConsumer

from backend.services.metric_service import MetricService
from backend.utils.logger import get_logger
from backend.utils.time_utils import now_utc
from backend.websocket.broadcasters import broadcast_metric_update
from config.database_config import async_session_factory
from config.kafka_config import kafka_config

logger = get_logger("all_events_consumer")

ORDER_CREATED = "order.created"
ORDER_CONFIRMED = "order.confirmed"
ORDER_CANCELLED = "order.cancelled"
PAYMENT_SUCCEEDED = "payment.succeeded"

PLATFORM_TOPICS = [ORDER_CREATED, ORDER_CONFIRMED, ORDER_CANCELLED, PAYMENT_SUCCEEDED]

METRIC_COUNT_KEYS = {
    ORDER_CREATED: "sales.orders.created",
    ORDER_CONFIRMED: "sales.orders.confirmed",
    ORDER_CANCELLED: "sales.orders.cancelled",
}


def _event_value(event: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in event and event[key] is not None:
            return event[key]
    return None


class AllEventsConsumer:
    """Consumes platform sales events and records them as analytics metrics."""

    def __init__(self) -> None:
        self._consumer: AIOKafkaConsumer | None = None
        self._running = False

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            *PLATFORM_TOPICS,
            bootstrap_servers=kafka_config["bootstrap_servers"],
            group_id="analytics-platform-events",
            auto_offset_reset=kafka_config["auto_offset_reset"],
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        )
        await self._consumer.start()
        self._running = True
        logger.info("All-events consumer started")

    async def stop(self) -> None:
        self._running = False
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
            logger.info("All-events consumer stopped")

    async def consume(self) -> None:
        if self._consumer is None:
            raise RuntimeError("Consumer not started")
        async for message in self._consumer:
            if not self._running:
                break
            try:
                await self.handle(message.topic, message.value)
            except Exception:
                logger.exception("Failed to process %s event", message.topic)

    async def handle(self, topic: str, event: dict[str, Any]) -> None:
        async with async_session_factory() as session:
            await self._process(session, topic, event)
            await session.commit()

    async def _process(self, session: Any, topic: str, event: dict[str, Any]) -> None:
        service = MetricService(session)
        if topic == PAYMENT_SUCCEEDED:
            amount = float(_event_value(event, "amount") or 0.0)
            if amount > 0:
                await self._record(service, "sales.revenue", amount, "amount", event)
        elif topic in METRIC_COUNT_KEYS:
            await self._record(service, METRIC_COUNT_KEYS[topic], 1.0, "count", event)
            if topic == ORDER_CREATED:
                gmv = float(_event_value(event, "totalAmount", "total_amount") or 0.0)
                if gmv > 0:
                    await self._record(
                        service, "sales.gmv.created", gmv, "amount", event
                    )

    async def _record(
        self,
        service: MetricService,
        key: str,
        value: float,
        unit: str,
        event: dict[str, Any],
    ) -> None:
        metric = await service.get_by_key(key)
        if metric is None:
            metric = await service.create_metric(
                name=key.replace(".", " ").title(),
                key=key,
                description="Derived from smart-ecommerce-platform events",
                unit=unit,
                data_type="float",
                aggregation_method="sum",
            )
        timestamp = _event_value(event, "timestamp")
        if timestamp is None:
            timestamp = now_utc()
        await service.record_value(metric.id, value, timestamp)
        broadcast_ts = (
            timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp)
        )
        await broadcast_metric_update(key, value, broadcast_ts)
