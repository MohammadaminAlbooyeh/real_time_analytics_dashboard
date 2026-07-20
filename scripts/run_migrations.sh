#!/bin/bash
# Run database migrations for new features

echo "Running Alembic migrations..."
cd "$(dirname "$0")/.."

alembic upgrade head

echo ""
echo "✅ Migrations complete. New tables created:"
echo "   - tenants (multi-tenant support)"
echo "   - retention_policies (data retention)"
echo "   - webhook_templates (custom webhook templating)"
echo "   - compliance_reports (GDPR/SOC2 reports)"
echo "   - encryption_keys (encryption at rest)"
echo ""
echo "Updated tables:"
echo "   - users (added tenant_id, sso_provider, sso_id)"
