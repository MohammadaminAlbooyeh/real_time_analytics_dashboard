"""add performance indexes

Revision ID: 003
Revises: 002
Create Date: 2025-01-01 00:02:00.000000
"""
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_time_series_metric_ts", "time_series_data", ["metric_id", "timestamp"])
    op.create_index("ix_alert_events_rule_status", "alert_events", ["rule_id", "status"])
    op.create_index("ix_dashboard_items_dashboard", "dashboard_items", ["dashboard_id"])


def downgrade():
    op.drop_index("ix_dashboard_items_dashboard")
    op.drop_index("ix_alert_events_rule_status")
    op.drop_index("ix_time_series_metric_ts")
