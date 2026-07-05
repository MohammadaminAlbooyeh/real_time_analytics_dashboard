# API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://api.analytics-dashboard.com`

## Authentication

All endpoints (except `/login`) require JWT authentication:

```
Authorization: Bearer <jwt_token>
```

## Endpoints

### Authentication

#### POST `/api/auth/login`
Login with credentials.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Users

#### GET `/api/v1/users/me`
Get current user information.

### Metrics

#### POST `/api/v1/metrics`
Create a new metric.

#### GET `/api/v1/metrics`
List all metrics.

#### GET `/api/v1/metrics/{metric_id}`
Get a specific metric.

#### POST `/api/v1/metrics/{metric_id}/data`
Record a data point.

### Analytics

#### GET `/api/v1/analytics/timeseries`
Get time-series data.

**Query Parameters:**
- `metric_id` (UUID)
- `start` (ISO8601)
- `end` (ISO8601)
- `interval` (str, default: "1m")

#### GET `/api/v1/analytics/summary/{metric_id}`
Get statistical summary.

#### POST `/api/v1/analytics/compare`
Compare metric performance across periods.

### Dashboards

#### POST `/api/v1/dashboards`
Create a dashboard.

#### GET `/api/v1/dashboards`
List dashboards.

#### GET `/api/v1/dashboards/{dashboard_id}`
Get a dashboard.

#### PUT `/api/v1/dashboards/{dashboard_id}`
Update a dashboard.

#### DELETE `/api/v1/dashboards/{dashboard_id}`
Delete a dashboard.

### Dashboard Items

#### POST `/api/v1/dashboards/{dashboard_id}/items`
Add item to dashboard.

#### GET `/api/v1/dashboards/{dashboard_id}/items`
List dashboard items.

#### DELETE `/api/v1/dashboards/{dashboard_id}/items/{item_id}`
Remove item from dashboard.

### Alerts

#### POST `/api/v1/alerts/rules`
Create an alert rule.

#### GET `/api/v1/alerts/rules`
List alert rules.

#### GET `/api/v1/alerts/events`
List alert events.

#### POST `/api/v1/alerts/events/{event_id}/resolve`
Resolve an alert.

### Data Sources

#### POST `/api/v1/datasources`
Create a data source.

#### GET `/api/v1/datasources`
List data sources.

#### PUT `/api/v1/datasources/{datasource_id}`
Update a data source.

#### DELETE `/api/v1/datasources/{datasource_id}`
Delete a data source.

### Reports

#### POST `/api/v1/reports`
Generate a report.

#### GET `/api/v1/reports`
List reports.

#### GET `/api/v1/reports/{report_id}/download`
Download a report.

### Export

#### POST `/api/v1/export`
Export metric data.

## WebSocket

### Connection
```
ws://localhost:8000/ws?token=<jwt_token>
```

### Events

#### Subscribe to Metric Updates
```json
{
  "type": "subscribe_metric",
  "metric_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Metric Update
```json
{
  "type": "metric_update",
  "metric_id": "550e8400-e29b-41d4-a716-446655440000",
  "value": 125.5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- 100 requests per minute per user for API endpoints
- 10 concurrent WebSocket connections per user

## Pagination

All list endpoints support:
- `skip` (int): Number of records to skip
- `limit` (int): Maximum records to return
