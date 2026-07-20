import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.compliance import ComplianceReport
from backend.utils.logger import get_logger
import json

logger = get_logger("compliance_service")


class ComplianceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_gdpr_report(self, tenant_id: uuid.UUID | None = None) -> ComplianceReport:
        """Generate a GDPR compliance report."""
        report_data = {
            "report_type": "GDPR",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tenant_id": str(tenant_id) if tenant_id else "all",
            "data_processing_activities": [
                {
                    "purpose": "Real-time analytics metric collection",
                    "data_categories": ["Metric values", "Timestamps", "Metric metadata"],
                    "legal_basis": "Consent / Legitimate Interest",
                    "retention_period": "90 days (configurable)",
                },
                {
                    "purpose": "User account management",
                    "data_categories": ["Email", "Username", "Authentication data"],
                    "legal_basis": "Contractual necessity",
                    "retention_period": "Duration of account + 1 year",
                },
                {
                    "purpose": "Alert notifications",
                    "data_categories": ["Alert events", "Notification preferences"],
                    "legal_basis": "Consent",
                    "retention_period": "1 year",
                },
            ],
            "data_subject_rights": {
                "right_to_access": True,
                "right_to_rectification": True,
                "right_to_erasure": True,
                "right_to_restrict_processing": True,
                "right_to_data_portability": True,
            },
            "technical_measures": [
                "Encryption at rest (AES-256-GCM)",
                "Encryption in transit (TLS)",
                "JWT authentication",
                "Role-based access control",
                "Audit logging",
            ],
        }
        report = ComplianceReport(
            report_type="gdpr",
            tenant_id=tenant_id,
            status="generated",
            report_data=json.dumps(report_data, default=str, indent=2),
            generated_at=datetime.now(timezone.utc),
        )
        self.session.add(report)
        await self.session.flush()
        logger.info(f"Generated GDPR compliance report {report.id}")
        return report

    async def generate_soc2_report(self, tenant_id: uuid.UUID | None = None) -> ComplianceReport:
        """Generate a SOC2 compliance report."""
        report_data = {
            "report_type": "SOC2",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tenant_id": str(tenant_id) if tenant_id else "all",
            "trust_service_criteria": {
                "security": {
                    "status": "compliant",
                    "controls": [
                        "Firewall and network segmentation",
                        "Intrusion detection",
                        "Access controls (RBAC)",
                        "Encryption in transit and at rest",
                    ],
                },
                "availability": {
                    "status": "compliant",
                    "controls": [
                        "Redundant infrastructure (Docker)",
                        "Health checks and auto-recovery",
                        "Database replication",
                        "Kafka message durability",
                    ],
                },
                "processing_integrity": {
                    "status": "compliant",
                    "controls": [
                        "Input validation",
                        "Data pipeline monitoring",
                        "Idempotent processing",
                        "Audit trail for data changes",
                    ],
                },
                "confidentiality": {
                    "status": "compliant",
                    "controls": [
                        "Data classification",
                        "Encryption at rest",
                        "Access logging",
                        "Multi-tenant isolation",
                    ],
                },
                "privacy": {
                    "status": "compliant",
                    "controls": [
                        "Data retention policies",
                        "Consent management",
                        "Data anonymization",
                        "Right to erasure support",
                    ],
                },
            },
            "monitoring_tools": ["Prometheus", "Grafana", "Audit logs"],
        }
        report = ComplianceReport(
            report_type="soc2",
            tenant_id=tenant_id,
            status="generated",
            report_data=json.dumps(report_data, default=str, indent=2),
            generated_at=datetime.now(timezone.utc),
        )
        self.session.add(report)
        await self.session.flush()
        logger.info(f"Generated SOC2 compliance report {report.id}")
        return report

    async def list_reports(
        self, report_type: str | None = None,
        tenant_id: uuid.UUID | None = None,
        skip: int = 0, limit: int = 50,
    ) -> list[ComplianceReport]:
        query = select(ComplianceReport)
        if report_type:
            query = query.where(ComplianceReport.report_type == report_type)
        if tenant_id:
            query = query.where(ComplianceReport.tenant_id == tenant_id)
        query = query.order_by(ComplianceReport.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_report(self, report_id: uuid.UUID) -> ComplianceReport | None:
        result = await self.session.execute(
            select(ComplianceReport).where(ComplianceReport.id == report_id)
        )
        return result.scalar_one_or_none()