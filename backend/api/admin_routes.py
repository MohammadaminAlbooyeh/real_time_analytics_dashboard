from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from backend.api.dependencies import get_db, get_admin_user
from backend.api.schemas import (
    TenantCreate, TenantResponse,
    RetentionPolicyCreate, RetentionPolicyResponse,
    WebhookTemplateCreate, WebhookTemplateResponse,
)
from backend.services.tenant_service import TenantService
from backend.services.retention_service import RetentionService
from backend.services.webhook_template_service import WebhookTemplateService
from backend.services.compliance_service import ComplianceService
from backend.services.encryption_service import EncryptionService
from backend.services.ml_service import MLService
from backend.models.user import User

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ──────────────────────────────────────────────
# Multi-Tenant Management
# ──────────────────────────────────────────────
@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    body: TenantCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = TenantService(session)
    existing = await service.get_by_domain(body.domain) if body.domain else None
    if existing:
        raise HTTPException(status_code=400, detail="Tenant with this domain already exists")
    return await service.create_tenant(name=body.name, domain=body.domain, settings_json=body.settings_json)


@router.get("/tenants", response_model=list[TenantResponse])
async def list_tenants(
    skip: int = 0, limit: int = 100,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = TenantService(session)
    return await service.list_tenants(skip=skip, limit=limit)


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = TenantService(session)
    tenant = await service.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = TenantService(session)
    deleted = await service.delete_tenant(tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"status": "deleted"}


# ──────────────────────────────────────────────
# Data Retention Policies
# ──────────────────────────────────────────────
@router.post("/retention-policies", response_model=RetentionPolicyResponse)
async def create_retention_policy(
    body: RetentionPolicyCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = RetentionService(session)
    return await service.create_policy(
        metric_id=body.metric_id,
        tenant_id=body.tenant_id,
        retention_days=body.retention_days,
    )


@router.get("/retention-policies", response_model=list[RetentionPolicyResponse])
async def list_retention_policies(
    skip: int = 0, limit: int = 100,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = RetentionService(session)
    return await service.list_policies(skip=skip, limit=limit)


@router.put("/retention-policies/{policy_id}", response_model=RetentionPolicyResponse)
async def update_retention_policy(
    policy_id: UUID, retention_days: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = RetentionService(session)
    policy = await service.update_policy(policy_id, retention_days=retention_days)
    if not policy:
        raise HTTPException(status_code=404, detail="Retention policy not found")
    return policy


@router.post("/retention-policies/{policy_id}/apply")
async def apply_retention_policy(
    policy_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = RetentionService(session)
    await service.update_policy(policy_id, enabled=True)
    deleted = await service.apply_retention()
    return {"status": "applied", "deleted_records": deleted}


@router.delete("/retention-policies/{policy_id}")
async def delete_retention_policy(
    policy_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = RetentionService(session)
    deleted = await service.delete_policy(policy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Retention policy not found")
    return {"status": "deleted"}


# ──────────────────────────────────────────────
# Webhook Templates
# ──────────────────────────────────────────────
@router.post("/webhook-templates", response_model=WebhookTemplateResponse)
async def create_webhook_template(
    body: WebhookTemplateCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = WebhookTemplateService(session)
    return await service.create_template(
        name=body.name, template_body=body.template_body,
        description=body.description, template_headers=body.template_headers,
        content_type=body.content_type, is_default=body.is_default,
    )


@router.get("/webhook-templates", response_model=list[WebhookTemplateResponse])
async def list_webhook_templates(
    skip: int = 0, limit: int = 100,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = WebhookTemplateService(session)
    return await service.list_templates(skip=skip, limit=limit)


@router.get("/webhook-templates/{template_id}")
async def get_webhook_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = WebhookTemplateService(session)
    tmpl = await service.get_template(template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return tmpl


@router.delete("/webhook-templates/{template_id}")
async def delete_webhook_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = WebhookTemplateService(session)
    deleted = await service.delete_template(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"status": "deleted"}


# ──────────────────────────────────────────────
# Compliance Reports (GDPR / SOC2)
# ──────────────────────────────────────────────
@router.post("/compliance/reports/gdpr")
async def generate_gdpr_report(
    tenant_id: UUID | None = Query(None),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = ComplianceService(session)
    report = await service.generate_gdpr_report(tenant_id=tenant_id)
    return {"id": str(report.id), "status": report.status, "report_type": report.report_type}


@router.post("/compliance/reports/soc2")
async def generate_soc2_report(
    tenant_id: UUID | None = Query(None),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = ComplianceService(session)
    report = await service.generate_soc2_report(tenant_id=tenant_id)
    return {"id": str(report.id), "status": report.status, "report_type": report.report_type}


@router.get("/compliance/reports")
async def list_compliance_reports(
    report_type: str | None = Query(None),
    tenant_id: UUID | None = Query(None),
    skip: int = 0, limit: int = 50,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = ComplianceService(session)
    reports = await service.list_reports(
        report_type=report_type, tenant_id=tenant_id,
        skip=skip, limit=limit,
    )
    return [
        {
            "id": str(r.id), "type": r.report_type,
            "status": r.status,
            "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            "created_at": r.created_at.isoformat(),
        }
        for r in reports
    ]


@router.get("/compliance/reports/{report_id}")
async def get_compliance_report(
    report_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = ComplianceService(session)
    report = await service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "id": str(report.id),
        "type": report.report_type,
        "status": report.status,
        "data": report.report_data,
        "generated_at": report.generated_at.isoformat() if report.generated_at else None,
    }


# ──────────────────────────────────────────────
# Encryption at Rest
# ──────────────────────────────────────────────
@router.post("/encryption/keys")
async def create_encryption_key(
    name: str, passphrase: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = EncryptionService(session)
    key = await service.create_key(name=name, passphrase=passphrase)
    return {"id": str(key.id), "name": key.name, "algorithm": key.algorithm}


@router.get("/encryption/keys")
async def list_encryption_keys(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = EncryptionService(session)
    keys = await service.list_keys()
    return [
        {"id": str(k.id), "name": k.name, "algorithm": k.algorithm,
         "is_active": k.is_active, "created_at": k.created_at.isoformat()}
        for k in keys
    ]


@router.post("/encryption/keys/{key_id}/rotate")
async def rotate_encryption_key(
    key_id: UUID, new_passphrase: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = EncryptionService(session)
    new_key = await service.rotate_key(key_id, new_passphrase)
    if not new_key:
        raise HTTPException(status_code=404, detail="Encryption key not found")
    return {"id": str(new_key.id), "name": new_key.name, "status": "rotated"}


# ──────────────────────────────────────────────
# ML / Anomaly Detection APIs
# ──────────────────────────────────────────────
@router.get("/ml/anomalies/{metric_id}")
async def detect_anomalies(
    metric_id: UUID,
    lookback_hours: int = Query(168),
    contamination: float = Query(0.05),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = MLService(session)
    anomalies = await service.detect_anomalies_isolation_forest(
        metric_id, lookback_hours=lookback_hours, contamination=contamination,
    )
    return {"metric_id": str(metric_id), "anomalies": anomalies, "count": len(anomalies)}


@router.get("/ml/forecast/{metric_id}")
async def forecast_metric(
    metric_id: UUID,
    forecast_hours: int = Query(24),
    lookback_hours: int = Query(336),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = MLService(session)
    forecasts = await service.forecast_values(
        metric_id, forecast_hours=forecast_hours, lookback_hours=lookback_hours,
    )
    return {"metric_id": str(metric_id), "forecasts": forecasts, "count": len(forecasts)}


@router.get("/ml/insights/{metric_id}")
async def get_ml_insights(
    metric_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    service = MLService(session)
    return await service.get_model_insights(metric_id)


# ──────────────────────────────────────────────
# Admin Status & Config
# ──────────────────────────────────────────────
@router.get("/status")
async def admin_status(
    current_user: User = Depends(get_admin_user),
):
    return {"status": "ok", "admin": True, "user": current_user.username}


@router.get("/tenant-info")
async def get_current_tenant_info(
    current_user: User = Depends(get_admin_user),
):
    return {
        "tenant_id": str(current_user.tenant_id) if current_user.tenant_id else None,
        "is_active": True,
    }


@router.get("/security-status")
async def get_security_status(
    current_user: User = Depends(get_admin_user),
):
    from config.settings import settings as app_settings

    return {
        "encryption_enabled": bool(app_settings.encryption_enabled),
        "encryption_method": "AES-256-GCM",
        "saml_enabled": bool(app_settings.saml_enabled),
        "saml_provider": app_settings.saml_idp_metadata_url or "local",
        "mfa_enabled": False,
    }


@router.get("/ml/config")
async def get_ml_config(
    current_user: User = Depends(get_admin_user),
):
    from config.settings import settings as app_settings

    return {
        "model_name": "scikit-learn",
        "default_contamination": app_settings.ml_anomaly_contamination,
        "max_lookback_hours": 336,
        "forecast_horizon": app_settings.ml_forecast_horizon,
        "anomaly_detection_enabled": True,
        "forecasting_enabled": True,
    }
