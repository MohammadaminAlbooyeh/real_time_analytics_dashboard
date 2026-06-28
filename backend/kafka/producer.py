import json
from aiokafka import AIOKafkaProducer
from config.kafka_config import kafka_config
from backend.utils.logger import get_logger

logger = get_logger("kafka_producer")


class AnalyticsKafkaProducer:
    def __init__(self):
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config["bootstrap_servers"],
            value_serializer=lambda v: json.dumps(v).encode(),
        )
        await self.producer.start()
        logger.info("Kafka producer started")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    async def send(self, topic: str, value: dict, key: str | None = None):
        if not self.producer:
            raise RuntimeError("Producer not started")
        key_bytes = key.encode() if key else None
        await self.producer.send(topic, value=value, key=key_bytes)
        logger.debug(f"Sent to {topic}: {value}")

    async def send_raw_data(self, metric_key: str, value: float, source_id: str, tags: dict | None = None):
        from datetime import datetime, timezone
        await self.send("analytics.raw.data", {
            "source_id": source_id,
            "metric_key": metric_key,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tags": tags or {},
        }, key=metric_key)

    async def send_alert(self, rule_id: str, metric_key: str, value: float,
                         threshold: float, severity: str, message: str):
        from datetime import datetime, timezone
        await self.send("analytics.alerts", {
            "rule_id": rule_id,
            "metric_key": metric_key,
            "value": value,
            "threshold": threshold,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, key=metric_key)
