"""create timescale hypertable

Revision ID: 002
Revises: 001
Create Date: 2025-01-01 00:01:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "time_series_data",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("metric_id", UUID(as_uuid=True), sa.ForeignKey("metrics.id"), nullable=False, index=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("tags_json", sa.String(500), nullable=True),
    )

    op.execute("SELECT create_hypertable('time_series_data', 'timestamp', if_not_exists => TRUE)")


def downgrade():
    op.drop_table("time_series_data")
