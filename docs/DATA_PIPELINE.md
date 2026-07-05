# Data Pipeline

## Overview

The data pipeline handles the flow of metrics from collection through storage and analysis.

```
Data Ingestion → Kafka → Processing → Storage → Analytics → Visualization
```

## Components

### 1. Data Ingestion

**Entry Points**:
- REST API: POST `/api/v1/metrics/{metric_id}/data`
- External Data Sources: HTTP, Database, Custom
- Event Streaming: Real-time events

**Data Format**:
```json
{
  "metric_id": "uuid",
  "value": 125.5,
  "timestamp": "2024-01-15T10:30:00Z",
  "tags": {
    "host": "server-1",
    "region": "us-east"
  }
}
```

### 2. Message Queue (Kafka)

**Topics**:
- `analytics.metrics`: Raw metric data
- `analytics.events`: System events
- `analytics.alerts`: Alert notifications

**Producers**:
- Backend API receives data
- External sources send data
- System events generated

**Consumers**:
- Data processor for aggregation
- Alert engine for rule evaluation
- WebSocket broadcaster for real-time

### 3. Processing

**Aggregation**:
- Time-based bucketing (1m, 5m, 1h, 1d)
- Statistical functions (min, max, avg, stddev, median)
- Percentage change calculation

**Deduplication**:
- Remove duplicate data points
- Handle out-of-order messages

**Data Quality**:
- Validate ranges
- Detect anomalies
- Mark invalid data

### 4. Storage

**Time-Series Database** (PostgreSQL + TimescaleDB):
- Raw metric data points
- Aggregated summaries
- Retention policies

**Cache Layer** (Redis):
- Recent metric values
- Aggregated results
- User sessions

**Key Tables**:
- `metrics`: Metric definitions
- `data_points`: Raw measurements
- `aggregations`: Pre-computed summaries
- `alert_events`: Alert history

### 5. Analytics Engine

**Real-Time Analysis**:
- Continuous metric evaluation
- Alert rule checking
- Anomaly detection

**Historical Analysis**:
- Period comparison
- Trend analysis
- Statistical summaries

### 6. Visualization

**Dashboard Display**:
- Real-time metric values
- Historical charts
- Alert status
- Performance indicators

**WebSocket Updates**:
- Push updates to connected clients
- Subscribe/unsubscribe patterns
- Selective delivery

## Data Flow Examples

### Example 1: Simple Metric Recording

```
1. API receives metric POST
   POST /api/v1/metrics/{id}/data
   
2. Validate and store in PostgreSQL
   INSERT INTO data_points (metric_id, value, timestamp)
   
3. Publish to Kafka
   kafka.metrics_topic.send(data)
   
4. Consumer processes
   Aggregate by time bucket
   Update Redis cache
   
5. WebSocket broadcasts
   Send to subscribed clients
   
6. Frontend updates charts
   Real-time display
```

### Example 2: Alert Evaluation

```
1. Metric data point recorded
2. Alert engine evaluates rule
   if value > threshold:
     Create alert event
3. Publish to alerts topic
4. Notification handler
   Send email/Slack/webhook
5. Alert status stored
6. Frontend shows alert
```

### Example 3: Analytics Query

```
1. Frontend requests timeseries
   GET /api/v1/analytics/timeseries
   ?metric_id=...&start=...&end=...
   
2. Backend queries cache first
   Try Redis for recent data
   
3. If not cached, query database
   SELECT * FROM aggregations
   WHERE metric_id = ? AND timestamp BETWEEN ? AND ?
   
4. Cache result in Redis
   SETEX key value TTL
   
5. Return to frontend
   Send JSON response
   
6. Frontend renders chart
```

## Data Retention

### Policy

| Type | Duration | Purpose |
|------|----------|---------|
| Raw metrics | 7 days | Detailed analysis |
| 1-hour aggregates | 30 days | Daily trends |
| 1-day aggregates | 1 year | Long-term analysis |
| Alert history | 90 days | Incident tracking |
| Events | 30 days | Audit trail |

### Archival

Old data can be archived to cost-effective storage:
```sql
-- Archive data older than 1 year
INSERT INTO archive.data_points
SELECT * FROM data_points
WHERE timestamp < NOW() - INTERVAL '1 year';

DELETE FROM data_points
WHERE timestamp < NOW() - INTERVAL '1 year';
```

## Performance Optimization

### Indexes

Critical indexes for performance:
```sql
CREATE INDEX idx_data_points_metric_timestamp 
ON data_points(metric_id, timestamp DESC);

CREATE INDEX idx_aggregations_metric_time
ON aggregations(metric_id, time_bucket DESC);

CREATE INDEX idx_alerts_metric_severity
ON alert_events(metric_id, severity);
```

### Caching Strategy

- **Hot Data**: Last 1 hour in Redis (TTL: 1 minute)
- **Warm Data**: Last 1 day in Redis (TTL: 5 minutes)
- **Cold Data**: Database only

### Query Optimization

- Use time-series specific queries
- Leverage TimescaleDB's time_bucket()
- Partition tables by time
- Use prepared statements

## Monitoring Pipeline Health

### Key Metrics

- Ingestion rate (metrics/sec)
- Processing latency (ms)
- Storage usage (GB)
- Cache hit rate (%)
- Alert latency (ms)

### Dashboards

Monitor in Prometheus/Grafana:
- Pipeline throughput
- Queue depth (Kafka consumer lag)
- Database performance
- Cache performance

### Alerts

Setup alerts for:
- High processing latency
- Queue buildup (consumer lag)
- Database connection issues
- Storage capacity
- Alert evaluation failures

## Troubleshooting

### Data Not Appearing

1. Check API received data
2. Verify Kafka topic
3. Check consumer processing
4. Verify database writes
5. Check Redis cache

### Slow Queries

1. Check index usage
2. Review execution plans
3. Consider pre-aggregation
4. Archive old data
5. Tune database parameters

### Lost Data

1. Check Kafka retention
2. Verify consumer offsets
3. Review database logs
4. Check disk space
5. Enable transaction logging

