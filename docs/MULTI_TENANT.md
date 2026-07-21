# Multi-Tenant Architecture

## Overview

The Real-Time Analytics Dashboard supports **multi-tenant isolation**, allowing a single deployment to serve multiple organizations or teams while keeping their data separate. Each tenant operates in its own isolated namespace with dedicated metrics, dashboards, alerts, and configuration settings.

### Architecture

Tenants are identified by a unique UUID and optionally associated with a domain name for automatic routing. The system uses a `tenant_id` foreign key across all major data models to enforce data isolation at the database level.

```
┌─────────────────────────────────────────────┐
│            Application Instance              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Tenant A  │  │ Tenant B  │  │ Tenant C  │  │
│  │ (Acme Co) │  │ (BetaInc) │  │ (Gamma)   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│       │              │              │        │
│       └──────────────┴──────────────┘        │
│                      │                       │
│              ┌───────┴────────┐              │
│              │  Shared Pool   │              │
│              │ (PostgreSQL)   │              │
│              └────────────────┘              │
└─────────────────────────────────────────────┘
```

### Features

- **Data Isolation**: Each tenant's data is isolated via `tenant_id` foreign keys
- **Domain-Based Routing**: Optional domain association per tenant
- **Per-Tenant Settings**: Custom JSON settings for each tenant
- **Admin-Only Management**: Tenant CRUD restricted to admin users
- **Scalable Design**: Supports hundreds of tenants on a single deployment

---

## Creating and Managing Tenants

### Tenant Model

| Field         | Type      | Description                                 |
|---------------|-----------|---------------------------------------------|
| `id`          | UUID      | Auto-generated unique identifier            |
| `name`        | String    | Tenant name (unique, required)              |
| `domain`      | String    | Associated domain name (unique, optional)   |
| `is_active`   | Boolean   | Whether the tenant is active (default: true)|
| `settings_json` | String  | JSON string for custom tenant configuration |
| `created_at`  | DateTime  | Timestamp of creation                       |
| `updated_at`  | DateTime  | Timestamp of last update                    |

### Creating a Tenant

```python
from backend.services.tenant_service import TenantService

service = TenantService(session)
tenant = await service.create_tenant(
    name="Acme Corporation",
    domain="acme.com",
    settings_json='{"theme": "dark", "timezone": "UTC"}',
)
```

### Listing Tenants

```python
tenants = await service.list_tenants(skip=0, limit=100)
```

### Retrieving a Tenant

```python
# By ID
tenant = await service.get_by_id(tenant_id)

# By Domain
tenant = await service.get_by_domain("acme.com")
```

### Updating a Tenant

```python
tenant = await service.update_tenant(
    tenant_id,
    name="Acme Corp (Updated)",
    settings_json='{"theme": "light"}',
)
```

### Deleting a Tenant

```python
deleted = await service.delete_tenant(tenant_id)
```

---

## Tenant Isolation Features

### Database-Level Isolation

All major entities include a `tenant_id` column:
- `metrics` → associated via user's tenant context
- `dashboards` → scoped to tenant
- `alerts` → scoped to tenant
- `retention_policies` → can be scoped per tenant
- `compliance_reports` → tagged with tenant_id

### Domain Resolution

The system can automatically resolve tenants by domain name:

```python
tenant = await service.get_by_domain(request.domain)
```

### Configuration

```python
# config/settings.py
multi_tenant_enabled: bool = True
default_tenant: str = "default"
```

### User Association

Users can be associated with a tenant via the `tenant_id` field on the User model.

---

## API Endpoints Reference

All multi-tenant management endpoints are under **`/api/v1/admin`** and require admin privileges.

### Create Tenant

```
POST /api/v1/admin/tenants
```

**Request Body:**
```json
{
  "name": "Acme Corporation",
  "domain": "acme.com",
  "settings_json": "{\"theme\": \"dark\"}"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Acme Corporation",
  "domain": "acme.com",
  "is_active": true,
  "created_at": "2026-07-21T00:00:00+00:00"
}
```

### List Tenants

```
GET /api/v1/admin/tenants?skip=0&limit=100
```

### Get Tenant

```
GET /api/v1/admin/tenants/{tenant_id}
```

### Delete Tenant

```
DELETE /api/v1/admin/tenants/{tenant_id}
```

**Response:**
```json
{
  "status": "deleted"
}
```

---

## Configuration Options

| Environment Variable       | Default   | Description                          |
|----------------------------|-----------|--------------------------------------|
| `MULTI_TENANT_ENABLED`     | `true`    | Enable/disable multi-tenant mode     |
| `DEFAULT_TENANT`           | `default` | Default tenant name for single-tenant mode |

### Example `.env` Configuration

```bash
MULTI_TENANT_ENABLED=true
DEFAULT_TENANT=default
```

---

## Database Schema

The `tenants` table is defined in `backend/models/tenant.py`:

```python
class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    settings_json: Mapped[str] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture overview
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Full API reference
- [COMPLIANCE.md](./COMPLIANCE.md) - Per-tenant compliance reports
- [DATA_RETENTION.md](./DATA_RETENTION.md) - Per-tenant retention policies
