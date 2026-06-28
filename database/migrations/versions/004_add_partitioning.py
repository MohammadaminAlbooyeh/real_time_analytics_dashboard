"""add time-based partitioning policy

Revision ID: 004
Revises: 003
Create Date: 2025-01-01 00:03:00.000000
"""
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "SELECT add_dimension('time_series_data', "
        "  create_hypertable_index => FALSE"
        ")"
    )
    op.execute(
        "SELECT add_retention_policy('time_series_data', INTERVAL '90 days')"
    )


def downgrade():
    op.execute("SELECT remove_retention_policy('time_series_data', if_exists => TRUE)")
