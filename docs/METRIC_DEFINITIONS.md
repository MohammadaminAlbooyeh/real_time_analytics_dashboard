# Metric Definitions Guide

## Overview

Metrics are the core units of measurement in the analytics dashboard. This guide explains how to define and use metrics effectively.

## Metric Properties

### Required Fields

- **Name**: Human-readable metric name (e.g., "API Response Time")
- **Key**: Unique identifier for programmatic access (e.g., "api_response_time")
- **Data Type**: Type of data being measured (numeric, string, boolean)
- **Unit**: Unit of measurement (ms, %, count, bytes, etc.)

### Optional Fields

- **Description**: Detailed explanation of what the metric measures
- **Aggregation Method**: How to combine values (avg, min, max, sum, count)
- **Tags**: Key-value pairs for categorization

## Data Types

### Numeric
- Integer or floating-point numbers
- Examples: response time, error count, CPU usage
- Supports aggregation and statistics

### String
- Text values
- Examples: region, service name, status
- Good for categorization and filtering

### Boolean
- True/False values
- Examples: service status, feature flags

### Gauge
- Current value at a point in time
- Examples: current user count, memory usage
- Reset each period

### Counter
- Monotonically increasing values
- Examples: total requests, total errors
- Never decrease

## Common Metrics

### Performance Metrics

| Metric | Key | Unit | Type |
|--------|-----|------|------|
| Response Time | response_time | ms | numeric |
| Request Throughput | request_throughput | req/s | numeric |
| Error Rate | error_rate | % | numeric |
| P95 Latency | p95_latency | ms | numeric |

### Availability Metrics

| Metric | Key | Unit | Type |
|--------|-----|------|------|
| Uptime | uptime | % | numeric |
| Service Health | service_health | status | string |
| Active Connections | active_connections | count | numeric |

### Business Metrics

| Metric | Key | Unit | Type |
|--------|-----|------|------|
| User Count | user_count | count | numeric |
| Revenue | revenue | USD | numeric |
| Conversion Rate | conversion_rate | % | numeric |

### Infrastructure Metrics

| Metric | Key | Unit | Type |
|--------|-----|------|------|
| CPU Usage | cpu_usage | % | numeric |
| Memory Usage | memory_usage | % | numeric |
| Disk Space | disk_space | GB | numeric |
| Network Traffic | network_traffic | Mbps | numeric |

## Creating Metrics via API

```bash
curl -X POST http://localhost:8000/api/v1/metrics \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Response Time",
    "key": "api_response_time",
    "description": "Average response time for API endpoints",
    "unit": "ms",
    "data_type": "numeric",
    "aggregation_method": "avg",
    "tags": {
      "category": "performance",
      "service": "api"
    }
  }'
```

## Recording Data

### Single Data Point

```bash
curl -X POST http://localhost:8000/api/v1/metrics/{metric_id}/data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "value": 125.5,
    "timestamp": "2024-01-15T10:30:00Z",
    "tags": {
      "endpoint": "/api/users",
      "method": "GET"
    }
  }'
```

### Batch Recording

```bash
curl -X POST http://localhost:8000/api/v1/metrics/{metric_id}/data/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"value": 100, "timestamp": "2024-01-15T10:30:00Z"},
      {"value": 120, "timestamp": "2024-01-15T10:35:00Z"},
      {"value": 150, "timestamp": "2024-01-15T10:40:00Z"}
    ]
  }'
```

## Best Practices

### Naming Conventions

1. **Be Descriptive**
   - Good: `api_endpoint_response_time`
   - Bad: `time`, `latency`

2. **Use Snake Case**
   - Good: `cpu_usage_percent`
   - Bad: `CPUUsagePercent`, `cpu-usage`

3. **Include Unit if Not Obvious**
   - Good: `response_time_ms`
   - Bad: `response_time` (ambiguous)

### Data Quality

1. **Consistent Units**
   - Always use the same unit for a metric
   - Document conversion factors if needed

2. **Reasonable Values**
   - Reject negative values for counts
   - Reject values outside expected ranges

3. **Proper Timestamps**
   - Use UTC timestamps
   - Ensure system clock is synchronized

### Tagging Strategy

Use tags to add dimensions:

```json
{
  "value": 125.5,
  "tags": {
    "service": "api",
    "endpoint": "/users",
    "method": "GET",
    "region": "us-east-1",
    "environment": "production"
  }
}
```

Benefits:
- Filter data by dimension
- Drill down into specific issues
- Create comparative reports

### Aggregation Selection

| Method | Use Case | Example |
|--------|----------|---------|
| avg | Central tendency | Response time |
| min | Optimistic scenario | Best latency |
| max | Worst case scenario | Peak latency |
| sum | Total quantity | Total requests |
| count | Frequency | Number of errors |
| stddev | Variability | Response time variance |

## Querying Metrics

### Get Summary Statistics

```bash
curl http://localhost:8000/api/v1/analytics/summary/{metric_id} \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "count": 1000,
  "min": 50.2,
  "max": 250.5,
  "avg": 125.3,
  "stddev": 45.2,
  "median": 120.0
}
```

### Get Time Series Data

```bash
curl "http://localhost:8000/api/v1/analytics/timeseries?metric_id={id}&start=2024-01-01&end=2024-01-15&interval=1h" \
  -H "Authorization: Bearer $TOKEN"
```

### Filter by Tags

```bash
curl "http://localhost:8000/api/v1/metrics/{metric_id}/data?tags[service]=api&tags[region]=us-east-1" \
  -H "Authorization: Bearer $TOKEN"
```

## Metric Lifecycle

### Creation
1. Define metric properties
2. Choose appropriate type and unit
3. Set aggregation method
4. Create via API or UI

### Usage
1. Start recording data
2. Monitor in dashboards
3. Create alerts based on thresholds
4. Analyze trends

### Maintenance
1. Review data quality
2. Adjust aggregation if needed
3. Update description/tags
4. Archive if no longer used

### Deprecation
1. Mark as deprecated
2. Migrate to new metric
3. Keep historical data
4. Remove from dashboards

## Examples

### Web Application

```json
{
  "metrics": [
    {
      "name": "Page Load Time",
      "key": "page_load_time",
      "unit": "ms",
      "type": "numeric",
      "aggregation": "avg"
    },
    {
      "name": "Error Count",
      "key": "error_count",
      "unit": "count",
      "type": "numeric",
      "aggregation": "sum"
    },
    {
      "name": "User Session Duration",
      "key": "session_duration",
      "unit": "seconds",
      "type": "numeric",
      "aggregation": "avg"
    }
  ]
}
```

### Infrastructure

```json
{
  "metrics": [
    {
      "name": "CPU Usage",
      "key": "cpu_usage",
      "unit": "%",
      "type": "numeric",
      "aggregation": "avg"
    },
    {
      "name": "Memory Usage",
      "key": "memory_usage",
      "unit": "%",
      "type": "numeric",
      "aggregation": "max"
    },
    {
      "name": "Disk I/O",
      "key": "disk_io",
      "unit": "MB/s",
      "type": "numeric",
      "aggregation": "avg"
    }
  ]
}
```
