# Data Retention Policies

## Overview

The Real-Time Analytics Dashboard provides **configurable data retention policies** that automatically manage the lifecycle of time-series data. Policies define how long metric data points should be kept before being automatically purged, helping to manage storage costs and comply with data governance requirements.

### Retention Architecture

```
┌──────────────┐    Schedule/Manual     ┌──────────────────┐
│  Admin User   │ ────────────────────▶│  Retention Service│
└──────────────┘                        │  (backend/services│
                                        │  /retention_service│
                                        └────────┬─────────┘
                                                 │
                                    ┌────────────▼─────────┐
                                    │  apply_retention()    │
                                    │  - Queries enabled    │
                                    │    policies           │
                                    │  - Deletes old data   │
                                    │    points             │
                                    └────────────┬─────────┘
                                                 │
                                    ┌────────────▼─────────┐
                                    │  TimeSeriesDataPoint  │
                                    │  (PostgreSQL table)   │
                                    └──────────────────────┘
```

### Features

- **Configurable Retention**: Set retention periods from 1 to 365 days
- **Scope Control**: Apply policies globally, per metric, or per tenant
- **Automatic Cleanup**: Scheduled background task applies all enabled policies
- **Manual Trigger**: Apply cleanup on-demand via API
- **Disable/Enable**: Toggle policies without deleting them

---

## Creating and Managing Policies

### Retention Policy Model

| Field            | Type      | Description                                 |
|------------------|-----------|---------------------------------------------|
| `id`             | UUID      | Auto-generated unique identifier            |
| `metric_id`      | UUID      | Optional metric scope (null = all metrics)  |
| `tenant_id`      | UUID      | Optional tenant scope (null = all tenants)  |
| `retention_days` | Integer   | Number of days to retain data (default: 90) |
| `enabled`        | Boolean   | Whether the policy is active (default: true)|
| `created_at`     | DateTime  | Timestamp of creation                       |
| `updated_at`     | DateTime  | Timestamp of last update                    |

### Creating a Policy

```python
from backend.services.retention_service import RetentionService

service = RetentionService(session)

# Global policy (all metrics, all tenants)
policy = await service.create_policy(retention_days=90)

# Policy for a specific metric
policy = await service.create_policy(
    metric_id=metric_id,
    retention_days=30,
)

# Policy for a specific tenant
policy = await service.create_policy(
    tenant_id=tenant_id,
    retention_days=60,
)
```

### Listing Policies

```python
policies = await service.list_policies(skip=0, limit=100)
```

### Updating a Policy

```python
# Change retention period
await service.update_policy(policy_id, retention_days=45)

# Disable a policy (without deleting)
await service.update_policy(policy_id, enabled=False)
```

### Deleting a Policy

```python
deleted = await service.delete_policy(policy_id)
```

---

## Automatic Cleanup

### How `apply_retention()` Works

1. Queries all enabled retention policies from the database
2. For each policy, calculates a cutoff timestamp: `now - retention_days`
3. Deletes all `TimeSeriesDataPoint` records older than the cutoff
4. If the policy has a `metric_id`, only data for that metric is deleted
5. Returns the total count of deleted records

```python
# Apply all enabled retention policies
deleted_count = await service.apply_retention()
print(f"Deleted {deleted_count} old data points")
```

### Background Task Integration

The retention cleanup can be scheduled as a periodic background task (see `backend/background_tasks/cleanup_tasks.py`):

```python
async def scheduled_retention_cleanup():
    """Periodically apply retention policies."""
    async with AsyncSession(engine) as session:
        service = RetentionService(session)
        deleted = await service.apply_retention()
        logger.info(f"Scheduled cleanup deleted {deleted} records")
```

### Policy Filtering During Cleanup

- Only policies with `enabled = True` are applied
- If `metric_id` is set, only data for that metric is deleted
- Data points newer than the cutoff are preserved

---

## Configuration Options

| Environment Variable       | Default | Description                              |
|----------------------------|---------|------------------------------------------|
| `RETENTION_DEFAULT_DAYS`   | `90`    | Default retention period for new policies|
| `RETENTION_MAX_DAYS`       | `365`   | Maximum allowed retention period         |

### Application Settings

```python
# config/settings.py
retention_default_days: int = 90
retention_max_days: int = 365
```

### Example `.env` Configuration

```bash
RETENTION_DEFAULT_DAYS=90
RETENTION_MAX_DAYS=365
```

---

## API Endpoints

All retention policy endpoints are under **`/api/v1/admin`** and require admin privileges.

### Create Retention Policy

```
POST /api/v1/admin/retention-policies
```

**Request Body:**
```json
{
  "metric_id": "uuid (optional)",
  "tenant_id": "uuid (optional)",
  "retention_days": 90
}
```

**Response:**
```json
{
  "id": "uuid",
  "metric_id": "uuid",
  "tenant_id": null,
  "retention_days": 90,
  "enabled": true,
  "created_at": "2026-07-21T00:00:00+00:00"
}
```

### List Retention Policies

```
GET /api/v1/admin/retention-policies?skip=0&limit=100
```

### Update Retention Policy

```
PUT /api/v1/admin/retention-policies/{policy_id}?retention_days=60
```

### Apply Retention Policy

```
POST /api/v1/admin/retention-policies/{policy_id}/apply
```

**Response:**
```json
{
  "status": "applied",
  "deleted_records": 1500
}
```

### Delete Retention Policy

```
DELETE /api/v1/admin/retention-policies/{policy_id}
```

**Response:**
```json
{
  "status": "deleted"
}
```

---

## Best Practices

1. **Start Conservative**: Begin with longer retention periods (e.g., 90 days) and adjust based on storage usage
2. **Scope Policies**: Use per-metric policies for high-volume metrics that need shorter retention
3. **Schedule Cleanup**: Run `apply_retention()` during off-peak hours
4. **Monitor Deletions**: Track the number of deleted records to ensure policies are working as expected
5. **Combine with Compliance**: Ensure retention periods align with GDPR/SOC2 data retention requirements

---

## Related Documentation

- [COMPLIANCE.md](./COMPLIANCE.md) - Compliance reporting
- [MULTI_TENANT.md](./MULTI_TENANT.md) - Per-tenant policy management
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [METRIC_DEFINITIONS.md](./METRIC_DEFINITIONS.md) - Metric management
