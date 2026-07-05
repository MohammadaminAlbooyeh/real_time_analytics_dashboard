# Kafka Configuration

## Overview

Kafka is used for real-time event streaming in the analytics dashboard.

## Topics

### analytics.metrics
- **Purpose**: Raw metric data points
- **Partitions**: 3
- **Replication Factor**: 1
- **Retention**: 7 days
- **Schema**: 
```json
{
  "metric_id": "uuid",
  "value": "float",
  "timestamp": "datetime",
  "tags": {"key": "value"}
}
```

### analytics.events
- **Purpose**: System and application events
- **Partitions**: 3
- **Replication Factor**: 1
- **Retention**: 30 days
- **Schema**:
```json
{
  "event_type": "string",
  "source": "string",
  "data": {},
  "timestamp": "datetime"
}
```

### analytics.alerts
- **Purpose**: Alert notifications and events
- **Partitions**: 2
- **Replication Factor**: 1
- **Retention**: 90 days
- **Schema**:
```json
{
  "alert_id": "uuid",
  "severity": "info|warning|critical",
  "message": "string",
  "timestamp": "datetime"
}
```

## Configuration

### Docker Compose
```yaml
kafka:
  image: confluentinc/cp-kafka:7.5.0
  environment:
    KAFKA_BOOTSTRAP_SERVERS: kafka:29092
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT_HOST://kafka:9092
```

### Environment Variables

In `.env`:
```
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_METRICS_TOPIC=analytics.metrics
KAFKA_EVENTS_TOPIC=analytics.events
KAFKA_ALERTS_TOPIC=analytics.alerts
KAFKA_CONSUMER_GROUP=analytics-consumer-group
```

## Creating Topics

```bash
# Create topic
kafka-topics.sh \
  --create \
  --bootstrap-server localhost:9092 \
  --topic analytics.metrics \
  --partitions 3 \
  --replication-factor 1

# List topics
kafka-topics.sh \
  --list \
  --bootstrap-server localhost:9092

# Describe topic
kafka-topics.sh \
  --describe \
  --topic analytics.metrics \
  --bootstrap-server localhost:9092
```

## Monitoring

### Console Consumer

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic analytics.metrics \
  --from-beginning
```

### Metrics

Monitor these key metrics:
- Consumer lag
- Producer throughput
- Topic replication status
- Broker disk usage

## Troubleshooting

### High Consumer Lag

1. Check consumer group status
2. Increase consumer instances
3. Increase partition count
4. Monitor CPU/memory on brokers

### Message Loss

1. Verify replication factor
2. Check broker status
3. Review retention settings
4. Check producer acknowledgment settings

### Connection Issues

```bash
# Test connection
nc -zv localhost 9092

# Check broker logs
docker-compose logs kafka
```
