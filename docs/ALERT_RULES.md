# Alert Rules Guide

## Overview

Alert rules allow you to define conditions that trigger notifications when metrics exceed thresholds.

## Rule Components

### Condition Types

- `greater_than`: Value > threshold
- `less_than`: Value < threshold
- `equal_to`: Value = threshold
- `between`: Value between min and max
- `change_percent`: % change exceeds threshold

### Severity Levels

- `info`: Informational alerts
- `warning`: Warning alerts (default)
- `critical`: Critical alerts requiring immediate action

### Notification Channels

- Email (via SendGrid)
- Slack (via Bot token)
- Webhook (HTTP POST)

## Creating Alert Rules

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/alerts/rules \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Response Time",
    "metric_id": "550e8400-e29b-41d4-a716-446655440000",
    "condition": "greater_than",
    "threshold": 500,
    "severity": "warning",
    "enabled": true,
    "evaluation_interval": "1m",
    "notification_channels": ["email", "slack"]
  }'
```

### Via UI

1. Navigate to Alerts page
2. Click "New Alert Rule"
3. Select metric
4. Define condition
5. Set severity and channels
6. Enable rule

## Examples

### Example 1: High API Latency

Alert when API response time exceeds 1 second:

```json
{
  "name": "API Latency High",
  "metric_id": "api_response_time_id",
  "condition": "greater_than",
  "threshold": 1000,
  "severity": "critical",
  "evaluation_interval": "5m"
}
```

### Example 2: Low Success Rate

Alert when success rate drops below 95%:

```json
{
  "name": "Low Success Rate",
  "metric_id": "success_rate_id",
  "condition": "less_than",
  "threshold": 95,
  "severity": "critical",
  "evaluation_interval": "1m"
}
```

### Example 3: Anomaly Detection

Alert when metric changes by >20%:

```json
{
  "name": "Anomaly Detection",
  "metric_id": "error_rate_id",
  "condition": "change_percent",
  "threshold": 20,
  "severity": "warning",
  "evaluation_interval": "5m"
}
```

## Notification Configuration

### Email Setup

Configure SendGrid API key in `.env`:
```
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
EMAIL_FROM_ADDRESS=alerts@your-domain.com
```

### Slack Setup

1. Create Slack app
2. Get bot token
3. Configure in `.env`:
```
SLACK_BOT_TOKEN=xoxb-xxxxxxxxx
SLACK_CHANNEL=alerts
```

### Webhook Setup

1. Provide webhook URL in rule configuration
2. Dashboard will POST alerts to URL
3. Expected response: 200-299 status code

Example payload:
```json
{
  "alert_id": "uuid",
  "alert_name": "High Latency",
  "severity": "critical",
  "metric": "api_response_time",
  "threshold": 1000,
  "actual_value": 1250,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Alert Escalation

Setup escalation rules:

```json
{
  "name": "Critical Alert Escalation",
  "alert_rule_id": "uuid",
  "escalation_steps": [
    {
      "wait_minutes": 5,
      "channels": ["slack"]
    },
    {
      "wait_minutes": 15,
      "channels": ["email", "sms"]
    }
  ]
}
```

## Best Practices

1. **Set Realistic Thresholds**
   - Use historical data to baseline
   - Avoid alert fatigue
   - Adjust based on feedback

2. **Use Meaningful Names**
   - Clear description of what's being monitored
   - Include metric name

3. **Appropriate Severity**
   - Critical: Immediate action required
   - Warning: Needs attention soon
   - Info: For tracking purposes

4. **Multiple Channels**
   - Critical: Use multiple channels
   - Warning: Primary channel
   - Info: Logging only

5. **Alert Hygiene**
   - Review and disable unused rules
   - Update thresholds seasonally
   - Document rule rationale

## Troubleshooting

### Alerts Not Triggering

1. Check rule is enabled
2. Verify evaluation interval
3. Check metric has recent data
4. Review condition logic

### Notification Not Delivered

1. Verify notification channel is configured
2. Check credentials (API keys, tokens)
3. Test channel configuration
4. Review service logs

### Alert Fatigue

1. Increase threshold
2. Increase evaluation interval
3. Add condition filters
4. Combine multiple conditions
