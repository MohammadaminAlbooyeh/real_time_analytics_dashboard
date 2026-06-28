import json
from aiokafka import AIOKafkaConsumer
from config.kafka_config import kafka_config, KAFKA_TOPIC_RAW_DATA, KAFKA_TOPIC_AGGREGATED_DATA, KAFKA_TOPIC_ALERTS
from backend.utils.logger import get_logger

logger = get_logger("kafka_consumer")


class AnalyticsKafkaConsumer:
    def __init__(self, on_message=None):
        self.consumer: AIOKafkaConsumer | None = None
        self.on_message = on_message
        self._running = False

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            KAFKA_TOPIC_RAW_DATA,
            KAFKA_TOPIC_AGGREGATED_DATA,
            KAFKA_TOPIC_ALERTS,
            bootstrap_servers=kafka_config["bootstrap_servers"],
            group_id=kafka_config["group_id"],
            auto_offset_reset=kafka_config["auto_offset_reset"],
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        await self.consumer.start()
        self._running = True
        logger.info("Kafka consumer started")

    async def stop(self):
        self._running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

    async def consume(self):
        if not self.consumer:
            raise RuntimeError("Consumer not started")
        async for msg in self.consumer:
            if not self._running:
                break
            try:
                logger.debug(f"Received {msg.topic}: {msg.value}")
                if self.on_message:
                    await self.on_message(msg.topic, msg.value)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
