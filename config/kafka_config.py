from config.settings import settings

KAFKA_TOPIC_RAW_DATA = "analytics.raw.data"
KAFKA_TOPIC_AGGREGATED_DATA = "analytics.aggregated.data"
KAFKA_TOPIC_ALERTS = "analytics.alerts"
KAFKA_TOPIC_METRICS = "analytics.metrics"

# smart-ecommerce-platform topics consumed by the all-events consumer
PLATFORM_TOPIC_ORDER_CREATED = "order.created"
PLATFORM_TOPIC_ORDER_CONFIRMED = "order.confirmed"
PLATFORM_TOPIC_ORDER_CANCELLED = "order.cancelled"
PLATFORM_TOPIC_PAYMENT_SUCCEEDED = "payment.succeeded"

kafka_config = {
    "bootstrap_servers": settings.kafka_bootstrap_servers,
    "group_id": settings.kafka_consumer_group,
    "auto_offset_reset": "earliest",
}
