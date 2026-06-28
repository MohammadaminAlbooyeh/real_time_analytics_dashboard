"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("is_admin", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "metrics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("data_type", sa.String(50), nullable=False, default="float"),
        sa.Column("aggregation_method", sa.String(50), nullable=False, default="avg"),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "data_sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("config_json", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), default="active"),
        sa.Column("last_collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "dashboards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("layout", JSONB(), nullable=True),
        sa.Column("is_public", sa.Boolean(), default=False),
        sa.Column("refresh_interval", sa.Integer(), default=30),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "alert_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metric_id", UUID(as_uuid=True), sa.ForeignKey("metrics.id"), nullable=False),
        sa.Column("condition", sa.String(20), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(20), default="warning"),
        sa.Column("enabled", sa.Boolean(), default=True),
        sa.Column("cooldown_minutes", sa.Integer(), default=5),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "dashboard_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("dashboard_id", UUID(as_uuid=True), sa.ForeignKey("dashboards.id"), nullable=False),
        sa.Column("metric_id", UUID(as_uuid=True), sa.ForeignKey("metrics.id"), nullable=False),
        sa.Column("chart_type", sa.String(50), nullable=False, default="line"),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("position_x", sa.Integer(), default=0),
        sa.Column("position_y", sa.Integer(), default=0),
        sa.Column("width", sa.Integer(), default=6),
        sa.Column("height", sa.Integer(), default=4),
        sa.Column("config", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "alert_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("rule_id", UUID(as_uuid=True), sa.ForeignKey("alert_rules.id"), nullable=False),
        sa.Column("status", sa.String(20), default="active"),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("acknowledged_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("alert_events")
    op.drop_table("dashboard_items")
    op.drop_table("alert_rules")
    op.drop_table("dashboards")
    op.drop_table("data_sources")
    op.drop_table("metrics")
    op.drop_table("users")
