# Secret Rotation Policy

## Overview

This document defines the policy and procedures for rotating secrets in the Real-Time Analytics Dashboard. Regular secret rotation is a critical security practice that limits the impact of compromised credentials.

## Rotation Schedule

| Secret | Rotation Frequency | Method |
|--------|-------------------|--------|
| `SECRET_KEY` | Every 3 months | `rotate_secrets.sh` |
| `JWT_SECRET_KEY` | Every 3 months | `rotate_secrets.sh` |
| Database password | Every 3 months | `rotate_secrets.sh` |
| Redis password | Every 3 months | `rotate_secrets.sh` |
| `ENCRYPTION_KEY` | Every 6 months | `rotate_secrets.sh` |
| `SENDGRID_API_KEY` | Every 6 months | Manual (Rotate via SendGrid UI) |
| `SLACK_BOT_TOKEN` | Every 6 months | Manual (Rotate via Slack UI) |
| SAML certificates | Yearly | Manual (Regenerate IDP certs) |
| SSL/TLS certificates | Yearly | Manual or cert-manager auto-renewal |

## Automated Rotation

### GitHub Actions Workflow

A scheduled workflow (`.github/workflows/secret-rotation.yml`) runs every 3 months:

- **Default mode**: Dry-run (preview changes without applying)
- **Production mode**: Set `dry_run: false` to apply changes
- Always creates a backup before applying

### Script

The `scripts/rotate_secrets.sh` script handles local rotation:

```bash
# Preview changes
./scripts/rotate_secrets.sh --dry-run

# Rotate with backup
./scripts/rotate_secrets.sh --backup

# Rotate specific env file
./scripts/rotate_secrets.sh --env-file /path/to/.env --backup
```

## Manual Rotation Procedure

### 1. Prepare

```bash
# Backup current environment
cp .env .env.backup.$(date +%Y%m%d)

# Review current secrets
grep -E "^(SECRET_KEY|JWT_SECRET_KEY|DATABASE_URL)" .env
```

### 2. Execute Rotation

```bash
# Dry run first
./scripts/rotate_secrets.sh --env-file .env --dry-run

# Apply rotation
./scripts/rotate_secrets.sh --env-file .env --backup
```

### 3. Update Kubernetes Secrets

If running on Kubernetes, update the secrets:

```bash
# Extract rotated values from .env
source .env

# Update Kubernetes secrets
kubectl patch secret analytics-secrets -n analytics -p="{\"stringData\":{\"SECRET_KEY\":\"$SECRET_KEY\"}}"
kubectl patch secret analytics-secrets -n analytics -p="{\"stringData\":{\"JWT_SECRET_KEY\":\"$JWT_SECRET_KEY\"}}"
kubectl patch secret analytics-secrets -n analytics -p="{\"stringData\":{\"DATABASE_URL\":\"$DATABASE_URL\"}}"

# Restart deployments
kubectl rollout restart -n analytics deployment/backend
```

### 4. Database Password Rotation

When rotating the database password:

```sql
-- As superuser, update the application user's password
ALTER USER analytics_user PASSWORD 'new_password';

-- Verify connectivity
\c analytics analytics_user
```

### 5. Verification

After rotation:

```bash
# Verify the application starts correctly
kubectl logs -n analytics -l app=backend --tail=50

# Run health check
kubectl exec -n analytics deployment/backend -- curl http://localhost:8000/health

# Check for auth errors in logs
kubectl logs -n analytics -l app=backend --tail=100 | grep -i "error\|fail\|auth"
```

## Emergency Rotation

If a secret compromise is suspected:

1. Rotate immediately regardless of schedule
2. Revoke the compromised credential at the source
3. Notify the team
4. Audit logs for unauthorized access
5. Document the incident

## Secrets That Cannot Be Rotated Automatically

- **SendGrid API Key**: Must be rotated via SendGrid admin console
- **Slack Bot Token**: Must be regenerated via Slack API dashboard
- **SAML/SSO Certificates**: Requires coordination with identity provider
- **SSL/TLS Certificates**: Use cert-manager for automatic renewal in K8s

## Compliance

This rotation policy supports compliance with:

- **SOC 2**: Access control and cryptographic key management requirements
- **GDPR**: Article 32 (Security of processing)
- **ISO 27001**: A.10.1 (Cryptographic controls)
- **PCI DSS**: Requirement 3 (Protect stored cardholder data) where applicable

## Audit Trail

All rotations are logged:

1. GitHub Actions workflow runs are preserved (90 days)
2. Backup files are retained (7 days)
3. Environment file modification timestamps are recorded
4. Kubernetes audit logs track secret updates

## Responsible Parties

- **DevOps Team**: Executes automated and emergency rotations
- **Security Team**: Reviews rotation logs and compliance
- **Engineering Lead**: Approves emergency rotations

---

**Last Updated**: 2026-07-21  
**Review Frequency**: Quarterly  
**Next Scheduled Rotation**: 2026-10-01
