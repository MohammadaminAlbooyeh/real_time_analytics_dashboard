from config.kafka_config import (
    KAFKA_TOPIC_RAW_DATA,
    KAFKA_TOPIC_AGGREGATED_DATA,
    KAFKA_TOPIC_ALERTS,
    KAFKA_TOPIC_METRICS,
)

TOPIC_CONFIGS = {
    KAFKA_TOPIC_RAW_DATA: {"num_partitions": 3, "replication_factor": 1},
    KAFKA_TOPIC_AGGREGATED_DATA: {"num_partitions": 3, "replication_factor": 1},
    KAFKA_TOPIC_ALERTS: {"num_partitions": 2, "replication_factor": 1},
    KAFKA_TOPIC_METRICS: {"num_partitions": 3, "replication_factor": 1},
}
