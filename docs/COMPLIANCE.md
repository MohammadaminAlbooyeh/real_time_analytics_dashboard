# Compliance Reporting

## Overview

The Real-Time Analytics Dashboard provides automated **compliance report generation** for two major regulatory frameworks: **GDPR** (General Data Protection Regulation) and **SOC2** (Service Organization Control 2). Reports can be generated on-demand or scheduled as background tasks.

### Supported Report Types

| Report Type | Framework                          | Use Case                                    |
|-------------|------------------------------------|---------------------------------------------|
| `gdpr`      | GDPR (EU Data Protection)          | Demonstrate data processing compliance      |
| `soc2`      | SOC2 (AICPA Trust Services)        | Show security, availability, and privacy    |

### Report Architecture

```
┌──────────┐    HTTP Request      ┌────────────────────┐
│  Client   │ ──────────────────▶│  Compliance Service │
└──────────┘                     │  (backend/services/ │
                                 │  compliance_service)│
                                 └──────────┬─────────┘
                                            │
                                    ┌───────▼────────┐
                                    │  PostgreSQL     │
                                    │ (compliance_    │
                                    │  reports table) │
                                    └────────────────┘
```

---

## GDPR Report Generation

### What the Report Contains

When a GDPR report is generated, it includes:

- **Data Processing Activities**: Categories of data collected, purposes, legal basis, and retention periods
- **Data Subject Rights**: Confirmation of support for all 5 GDPR rights (access, rectification, erasure, restrict processing, data portability)
- **Technical Measures**: Encryption, authentication, access control, and audit logging details

### GDPR Report Data Structure

```json
{
  "report_type": "GDPR",
  "generated_at": "2026-07-21T12:00:00+00:00",
  "tenant_id": "all",
  "data_processing_activities": [
    {
      "purpose": "Real-time analytics metric collection",
      "data_categories": ["Metric values", "Timestamps", "Metric metadata"],
      "legal_basis": "Consent / Legitimate Interest",
      "retention_period": "90 days (configurable)"
    }
  ],
  "data_subject_rights": {
    "right_to_access": true,
    "right_to_rectification": true,
    "right_to_erasure": true,
    "right_to_restrict_processing": true,
    "right_to_data_portability": true
  },
  "technical_measures": [
    "Encryption at rest (AES-256-GCM)",
    "Encryption in transit (TLS)",
    "JWT authentication",
    "Role-based access control",
    "Audit logging"
  ]
}
```

---

## SOC2 Report Generation

### What the Report Contains

SOC2 reports evaluate the system against the AICPA Trust Services Criteria:

| Criterion              | Default Status | Key Controls                              |
|------------------------|----------------|-------------------------------------------|
| **Security**           | Compliant      | Firewall, IDS, RBAC, Encryption           |
| **Availability**       | Compliant      | Redundant infra, Health checks, Replication|
| **Processing Integrity** | Compliant    | Input validation, Pipeline monitoring     |
| **Confidentiality**    | Compliant      | Data classification, Encryption, Isolation |
| **Privacy**            | Compliant      | Retention policies, Consent management    |

### SOC2 Report Data Structure

```json
{
  "report_type": "SOC2",
  "generated_at": "2026-07-21T12:00:00+00:00",
  "trust_service_criteria": {
    "security": {
      "status": "compliant",
      "controls": [
        "Firewall and network segmentation",
        "Intrusion detection",
        "Access controls (RBAC)",
        "Encryption in transit and at rest"
      ]
    }
  },
  "monitoring_tools": ["Prometheus", "Grafana", "Audit logs"]
}
```

---

## Report Management

### Generating a Report (Service Layer)

```python
from backend.services.compliance_service import ComplianceService

service = ComplianceService(session)

# Generate GDPR report (all tenants)
gdpr_report = await service.generate_gdpr_report()

# Generate GDPR report for a specific tenant
gdpr_report = await service.generate_gdpr_report(tenant_id=tenant_id)

# Generate SOC2 report
soc2_report = await service.generate_soc2_report()

# Generate SOC2 report for a specific tenant
soc2_report = await service.generate_soc2_report(tenant_id=tenant_id)
```

### Listing Reports

```python
# List all reports
reports = await service.list_reports()

# Filter by type
gdpr_reports = await service.list_reports(report_type="gdpr")

# Filter by tenant
tenant_reports = await service.list_reports(tenant_id=tenant_id)

# With pagination
reports = await service.list_reports(skip=0, limit=50)
```

### Getting a Report

```python
report = await service.get_report(report_id)
```

---

## API Endpoints

All compliance endpoints are under **`/api/v1/admin`** and require admin privileges.

### Generate GDPR Report

```
POST /api/v1/admin/compliance/reports/gdpr?tenant_id=uuid
```

**Response:**
```json
{
  "id": "uuid",
  "status": "generated",
  "report_type": "gdpr"
}
```

### Generate SOC2 Report

```
POST /api/v1/admin/compliance/reports/soc2?tenant_id=uuid
```

### List Compliance Reports

```
GET /api/v1/admin/compliance/reports?report_type=gdpr&tenant_id=uuid&skip=0&limit=50
```

**Response:**
```json
[
  {
    "id": "uuid",
    "type": "gdpr",
    "status": "generated",
    "generated_at": "2026-07-21T12:00:00+00:00",
    "created_at": "2026-07-21T12:00:00+00:00"
  }
]
```

### Get Compliance Report

```
GET /api/v1/admin/compliance/reports/{report_id}
```

**Response:**
```json
{
  "id": "uuid",
  "type": "gdpr",
  "status": "generated",
  "data": "{...report JSON content...}",
  "generated_at": "2026-07-21T12:00:00+00:00"
}
```

---

## Configuration

Compliance reports reference the following configuration:

| Environment Variable     | Default | Description                              |
|--------------------------|---------|------------------------------------------|
| `ENCRYPTION_ENABLED`     | `false` | Encryption status included in reports    |
| `MULTI_TENANT_ENABLED`   | `true`  | Multi-tenant status included in reports  |
| `RETENTION_DEFAULT_DAYS` | `90`    | Default data retention period in reports |

---

## Related Documentation

- [ENCRYPTION.md](./ENCRYPTION.md) - Encryption at rest details
- [DATA_RETENTION.md](./DATA_RETENTION.md) - Data retention policies
- [MULTI_TENANT.md](./MULTI_TENANT.md) - Multi-tenant architecture
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
