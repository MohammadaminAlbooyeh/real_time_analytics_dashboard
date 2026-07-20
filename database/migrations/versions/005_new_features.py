"""add new feature tables (multi-tenant, retention, webhook templates, compliance, encryption)

Revision ID: 005
Revises: 004
Create Date: 2025-06-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    # Tenants table
    op.create_table(
        "tenants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("domain", sa.String(255), unique=True, nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("settings_json", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Add tenant_id and SSO fields to users
    op.add_column("users", sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=True, index=True))
    op.add_column("users", sa.Column("sso_provider", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("sso_id", sa.String(255), nullable=True))

    # Retention policies table
    op.create_table(
        "retention_policies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("metric_id", UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("retention_days", sa.Integer(), nullable=False, default=90),
        sa.Column("enabled", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Webhook templates table
    op.create_table(
        "webhook_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("template_body", sa.Text(), nullable=False),
        sa.Column("template_headers", sa.String(2000), nullable=True),
        sa.Column("content_type", sa.String(100), default="application/json"),
        sa.Column("is_default", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Compliance reports table
    op.create_table(
        "compliance_reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("report_data", sa.Text(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Encryption keys table
    op.create_table(
        "encryption_keys",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_data", sa.LargeBinary(), nullable=False),
        sa.Column("algorithm", sa.String(50), default="AES-256-GCM"),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("encryption_keys")
    op.drop_table("compliance_reports")
    op.drop_table("webhook_templates")
    op.drop_table("retention_policies")
    op.drop_column("users", "sso_id")
    op.drop_column("users", "sso_provider")
    op.drop_column("users", "tenant_id")
    op.drop_table("tenants")
