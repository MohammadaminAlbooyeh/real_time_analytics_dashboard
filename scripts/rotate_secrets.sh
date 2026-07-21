#!/bin/bash
# =============================================================================
# Secrets Rotation Script for Real-Time Analytics Dashboard
# =============================================================================
# This script generates new secrets and updates the .env file.
# It rotates: SECRET_KEY, JWT secrets, database passwords, and API keys.
#
# Usage: ./scripts/rotate_secrets.sh [--env-file PATH] [--dry-run] [--backup]
#   --env-file PATH  Path to .env file (default: ./.env)
#   --dry-run        Print new secrets without writing
#   --backup         Backup existing .env before rotating
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

ENV_FILE="${PROJECT_DIR}/.env"
DRY_RUN=false
DO_BACKUP=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --env-file) ENV_FILE="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        --backup) DO_BACKUP=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

if [ ! -f "$ENV_FILE" ] && [ "$DRY_RUN" = false ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}⚠️  .env not found. Creating from .env.example...${NC}"
        cp .env.example "$ENV_FILE"
    else
        echo -e "${RED}❌ .env file not found and no .env.example to copy${NC}"
        exit 1
    fi
fi

# ── Helper Functions ─────────────────────────────────────────────────────────

generate_secret_key() {
    # Generate a 32-byte hex key (64 chars)
    openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))"
}

generate_jwt_secret() {
    openssl rand -base64 48 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(48))"
}

generate_db_password() {
    openssl rand -base64 24 2>/dev/null | tr -d '/+=' | cut -c1-24 || python3 -c "import secrets; print(secrets.token_urlsafe(18)[:24])"
}

generate_api_key() {
    openssl rand -hex 20 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(20))"
}

generate_fernet_key() {
    python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null
}

rotate_value() {
    local key="$1"
    local value="$2"
    local file="$3"

    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY-RUN] Would set ${key}=${value}"
        return 0
    fi

    # Use sed to replace the value (works on macOS and Linux)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS requires backup extension
        sed -i '' "s|^${key}=.*|${key}=${value}|" "$file" 2>/dev/null || true
    else
        sed -i "s|^${key}=.*|${key}=${value}|" "$file" 2>/dev/null || true
    fi
}

# ── Main Rotation Logic ──────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════════════"
echo "  Secrets Rotation"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Environment file: $ENV_FILE"
echo "  Dry run:         $DRY_RUN"
echo "  Backup:          $DO_BACKUP"
echo ""

# Backup existing .env
if [ "$DO_BACKUP" = true ] && [ "$DRY_RUN" = false ] && [ -f "$ENV_FILE" ]; then
    BACKUP_FILE="${ENV_FILE}.backup-$(date +%Y%m%d-%H%M%S)"
    cp "$ENV_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✅ Backed up to $BACKUP_FILE${NC}"
fi

# Generate new values
NEW_SECRET_KEY=$(generate_secret_key)
NEW_JWT_SECRET=$(generate_jwt_secret)
NEW_DB_PASSWORD=$(generate_db_password)
NEW_SENDGRID_KEY=$(generate_api_key)
NEW_SLACK_TOKEN=$(generate_api_key)
NEW_ENCRYPTION_KEY=$(generate_fernet_key)
NEW_REDIS_PASSWORD=$(generate_db_password)

echo "  Rotating secrets..."
echo ""

# Rotate each value in the .env file
# Secret Key
if grep -q "^SECRET_KEY=" "$ENV_FILE" 2>/dev/null; then
    rotate_value "SECRET_KEY" "$NEW_SECRET_KEY" "$ENV_FILE"
    echo -e "  ${GREEN}✅ SECRET_KEY rotated${NC}"
else
    echo "SECRET_KEY=${NEW_SECRET_KEY}" >> "$ENV_FILE"
    echo -e "  ${GREEN}✅ SECRET_KEY added${NC}"
fi

# JWT Secret - if JWT_SECRET_KEY exists
if grep -q "^JWT_SECRET_KEY=" "$ENV_FILE" 2>/dev/null; then
    rotate_value "JWT_SECRET_KEY" "$NEW_JWT_SECRET" "$ENV_FILE"
    echo -e "  ${GREEN}✅ JWT_SECRET_KEY rotated${NC}"
fi

# JWT Algorithm (keep as is)
# JWT Expiration (keep as is)

# Database password
if grep -q "^DATABASE_URL=" "$ENV_FILE" 2>/dev/null; then
    # Extract the URL parts and replace password
    CURRENT_URL=$(grep "^DATABASE_URL=" "$ENV_FILE" | cut -d= -f2-)
    # Replace password in URL - assumes format: postgresql+asyncpg://user:password@host:port/db
    NEW_URL=$(echo "$CURRENT_URL" | sed "s|://[^:]*:[^@]*@|://analytics_user:${NEW_DB_PASSWORD}@|")
    rotate_value "DATABASE_URL" "$NEW_URL" "$ENV_FILE"
    echo -e "  ${GREEN}✅ DATABASE_URL rotated${NC}"
fi

# Redis password
if grep -q "^REDIS_URL=" "$ENV_FILE" 2>/dev/null; then
    # If Redis URL has password format
    if grep -q "^REDIS_URL.*://.*:.*@" "$ENV_FILE" 2>/dev/null; then
        CURRENT_REDIS_URL=$(grep "^REDIS_URL=" "$ENV_FILE" | cut -d= -f2-)
        NEW_REDIS_URL=$(echo "$CURRENT_REDIS_URL" | sed "s|://[^:]*:[^@]*@|://default:${NEW_REDIS_PASSWORD}@|")
        rotate_value "REDIS_URL" "$NEW_REDIS_URL" "$ENV_FILE"
    fi
fi

# SendGrid API Key
if grep -q "^SENDGRID_API_KEY=" "$ENV_FILE" 2>/dev/null; then
    rotate_value "SENDGRID_API_KEY" "SG.${NEW_SENDGRID_KEY}" "$ENV_FILE"
    echo -e "  ${GREEN}✅ SENDGRID_API_KEY rotated${NC}"
fi

# Slack Bot Token
if grep -q "^SLACK_BOT_TOKEN=" "$ENV_FILE" 2>/dev/null; then
    rotate_value "SLACK_BOT_TOKEN" "xoxb-${NEW_SLACK_TOKEN}" "$ENV_FILE"
    echo -e "  ${GREEN}✅ SLACK_BOT_TOKEN rotated${NC}"
fi

# Encryption Key
if grep -q "^ENCRYPTION_KEY=" "$ENV_FILE" 2>/dev/null; then
    rotate_value "ENCRYPTION_KEY" "$NEW_ENCRYPTION_KEY" "$ENV_FILE"
    echo -e "  ${GREEN}✅ ENCRYPTION_KEY rotated${NC}"
fi

# Update docker-compose.yml if SECRET_KEY or DB password changed there
if [ -f "docker-compose.yml" ] && [ "$DRY_RUN" = false ]; then
    echo ""
    echo "  Checking docker-compose.yml for inline secrets..."

    # Update SECRET_KEY in docker-compose
    if grep -q "SECRET_KEY:" docker-compose.yml 2>/dev/null; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|SECRET_KEY:.*|SECRET_KEY: ${NEW_SECRET_KEY}|" docker-compose.yml
        else
            sed -i "s|SECRET_KEY:.*|SECRET_KEY: ${NEW_SECRET_KEY}|" docker-compose.yml
        fi
        echo -e "  ${GREEN}✅ docker-compose.yml SECRET_KEY updated${NC}"
    fi

    # Update DB password in DATABASE_URL in docker-compose
    if grep -q "DATABASE_URL:" docker-compose.yml 2>/dev/null; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|postgresql+asyncpg://analytics_user:analytics_password@|postgresql+asyncpg://analytics_user:${NEW_DB_PASSWORD}@|" docker-compose.yml
        else
            sed -i "s|postgresql+asyncpg://analytics_user:analytics_password@|postgresql+asyncpg://analytics_user:${NEW_DB_PASSWORD}@|" docker-compose.yml
        fi
        echo -e "  ${GREEN}✅ docker-compose.yml DATABASE_URL updated${NC}"
    fi

    # Update POSTGRES_PASSWORD
    if grep -q "POSTGRES_PASSWORD:" docker-compose.yml 2>/dev/null; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|POSTGRES_PASSWORD:.*|POSTGRES_PASSWORD: ${NEW_DB_PASSWORD}|" docker-compose.yml
        else
            sed -i "s|POSTGRES_PASSWORD:.*|POSTGRES_PASSWORD: ${NEW_DB_PASSWORD}|" docker-compose.yml
        fi
        echo -e "  ${GREEN}✅ docker-compose.yml POSTGRES_PASSWORD updated${NC}"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Rotation Complete"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Rotated secrets:"
echo "    - SECRET_KEY"
echo "    - DATABASE_URL password"
echo "    - SENDGRID_API_KEY"
echo "    - SLACK_BOT_TOKEN"
echo "    - ENCRYPTION_KEY"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}⚠️  Dry-run mode - no files were modified${NC}"
else
    echo -e "${GREEN}✅ Secrets rotated successfully${NC}"
fi

# Show new SECRET_KEY for reference
echo ""
echo "  New SECRET_KEY (first 20 chars): ${NEW_SECRET_KEY:0:20}..."
echo "  New DB password: ${NEW_DB_PASSWORD}"
echo ""

echo "⚠️  IMPORTANT:"
echo "   - Restart all services after rotation"
echo "   - If using docker-compose: docker-compose down && docker-compose up -d"
echo "   - Any services using old secrets will fail until restarted"
echo "   - Ensure database users are updated with the new password"
echo ""
