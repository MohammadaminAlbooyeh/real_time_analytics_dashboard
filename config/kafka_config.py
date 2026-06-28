from config.settings import settings

KAFKA_TOPIC_RAW_DATA = "analytics.raw.data"
KAFKA_TOPIC_AGGREGATED_DATA = "analytics.aggregated.data"
KAFKA_TOPIC_ALERTS = "analytics.alerts"
KAFKA_TOPIC_METRICS = "analytics.metrics"

kafka_config = {
    "bootstrap_servers": settings.kafka_bootstrap_servers,
    "group_id": settings.kafka_consumer_group,
    "auto_offset_reset": "earliest",
}
