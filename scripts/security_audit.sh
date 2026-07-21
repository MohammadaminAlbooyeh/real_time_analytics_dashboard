#!/bin/bash
# =============================================================================
# Security Audit Script for Real-Time Analytics Dashboard
# =============================================================================
# Usage: ./scripts/security_audit.sh [--json] [--quiet]
#   --json    Output results in JSON format
#   --quiet   Only output failures
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

OUTPUT_JSON=false
QUIET=false
FAILURES=0
WARNINGS=0
PASSES=0
REPORT_FILE="security-audit-report-$(date +%Y%m%d-%H%M%S).txt"
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

while [[ $# -gt 0 ]]; do
    case "$1" in --json) OUTPUT_JSON=true; shift ;; --quiet) QUIET=true; shift ;; *) echo "Unknown: $1"; exit 1 ;; esac
done

pass() { PASSES=$((PASSES+1)); $QUIET && return 0; echo -e "  ${GREEN}[PASS]${NC} $1"; }
warn() { WARNINGS=$((WARNINGS+1)); $QUIET && return 0; echo -e "  ${YELLOW}[WARN]${NC} $1"; }
fail() { FAILURES=$((FAILURES+1)); echo -e "  ${RED}[FAIL]${NC} $1"; }
section() { echo ""; echo "══════════════════════════════════════════════════"; echo "  $1"; echo "══════════════════════════════════════════════════"; }

# ── 1. Default / Weak Passwords ──────────────────────────────────────────────
section "1. Default / Weak Passwords"
check_default_passwords() {
    local found=0
    if [ -f ".env.example" ] && grep -qi "your-secret-key\|change-me\|your-" .env.example 2>/dev/null; then
        warn ".env.example has placeholder secrets (expected)"
    fi
    if [ -f "docker-compose.yml" ] && grep -qi "analytics_password\|password\|dev-secret-key" docker-compose.yml 2>/dev/null; then
        fail "docker-compose.yml contains default/weak passwords"; found=1
    else
        pass "docker-compose.yml has no default passwords"
    fi
    if [ -f ".env" ]; then
        if grep -qi "your-secret-key\|change-me\|password\|dev-secret" .env 2>/dev/null; then
            fail ".env contains default/weak secrets"; found=1
        else
            pass ".env has no default secrets"
        fi
    else
        warn ".env not found"
    fi
    return $found
}
check_default_passwords

# ── 2. Sensitive File Permissions ────────────────────────────────────────────
section "2. Sensitive File Permissions"
check_permissions() {
    local found=0 perms
    if [ -f ".env" ]; then
        perms=$(stat -f "%OLp" .env 2>/dev/null || stat -c "%a" .env 2>/dev/null)
        if [ "$perms" != "600" ] && [ "$perms" != "400" ]; then
            fail ".env permissions $perms (expected 600)"; found=1
        else
            pass ".env permissions $perms"
        fi
    fi
    if [ -d "nginx/ssl" ]; then
        for f in nginx/ssl/key.pem nginx/ssl/*.key; do
            [ -f "$f" ] || continue
            perms=$(stat -f "%OLp" "$f" 2>/dev/null || stat -c "%a" "$f" 2>/dev/null)
            if [ "$perms" != "600" ] && [ "$perms" != "400" ] && [ "$perms" != "440" ]; then
                fail "$f permissions $perms (expected 600)"; found=1
            else
                pass "$f permissions $perms"
            fi
        done
    fi
    return $found
}
check_permissions

# ── 3. Exposed Secrets ──────────────────────────────────────────────────────
section "3. Exposed Secrets"
check_exposed_secrets() {
    local found=0
    if [ ! -f ".env.example" ]; then warn ".env.example not found"; return 1; fi
    local patterns=("sk-[a-zA-Z0-9]" "ghp_[a-zA-Z0-9]" "xox[baprs]-" "AKIA[A-Z0-9]{16}" "SG\.[a-zA-Z0-9]")
    for p in "${patterns[@]}"; do
        if grep -Eq "$p" .env.example 2>/dev/null; then
            fail "Real secret found in .env.example matching: $p"; found=1
        fi
    done
    [ $found -eq 0 ] && pass "No exposed secrets in .env.example"
    return $found
}
check_exposed_secrets

# ── 4. HTTPS Configuration ───────────────────────────────────────────────────
section "4. HTTPS Configuration"
check_https_config() {
    local found=0
    if [ -f "nginx/conf.d/default.conf" ]; then
        grep -q "listen 443 ssl" nginx/conf.d/default.conf 2>/dev/null && pass "HTTPS (443) configured" || { fail "HTTPS not configured"; found=1; }
        grep -q "ssl_certificate" nginx/conf.d/default.conf 2>/dev/null && pass "SSL certs configured" || { fail "SSL certs not configured"; found=1; }
        grep -q "TLSv1.2" nginx/conf.d/default.conf 2>/dev/null && pass "TLS 1.2+ enforced" || { fail "TLS not restricted"; found=1; }
        grep -q "Strict-Transport-Security" nginx/conf.d/default.conf 2>/dev/null && pass "HSTS configured" || warn "HSTS missing"
    else
        fail "default.conf not found"; found=1
    fi
    if [ -f "nginx/ssl/cert.pem" ] && [ -f "nginx/ssl/key.pem" ]; then
        pass "SSL cert files exist"
        if command -v openssl &>/dev/null; then
            expiry=$(openssl x509 -enddate -noout -in nginx/ssl/cert.pem 2>/dev/null | cut -d= -f2)
            [ -n "$expiry" ] && pass "SSL cert expires: $expiry"
        fi
    else
        warn "SSL cert files not found (run scripts/generate_ssl.sh)"
    fi
    return $found
}
check_https_config

# ── 5. Open Ports ────────────────────────────────────────────────────────────
section "5. Open Ports"
check_open_ports() {
    local found=0
    if command -v lsof &>/dev/null; then
        ports=$(lsof -iTCP -sTCP:LISTEN -P -n 2>/dev/null | awk '{print $9}' | grep -E ':\d+' | sort -u)
        if [ -n "$ports" ]; then
            echo "$ports" | while read -r p; do echo "    - $p"; done
            echo "$ports" | grep -q ":5432" && warn "PostgreSQL 5432 exposed (should be internal)"
            echo "$ports" | grep -q ":6379" && warn "Redis 6379 exposed (should be internal)"
            echo "$ports" | grep -q ":9092" && warn "Kafka 9092 exposed (should be internal)"
            echo "$ports" | grep -q ":2181" && warn "ZooKeeper 2181 exposed (should be internal)"
        fi
    else
        warn "No port-scanning tool (lsof) found"
    fi
    if [ -f "docker-compose.yml" ] && grep -q "5432:5432\|6379:6379\|9092:9092\|2181:2181" docker-compose.yml 2>/dev/null; then
        warn "Internal ports exposed to host in docker-compose.yml"
    else
        pass "No internal ports exposed in docker-compose.yml"
    fi
    return $found
}
check_open_ports

# ── 6. Dependency Vulnerabilities ────────────────────────────────────────────
section "6. Dependency Vulnerabilities"
if [ -f "requirements.txt" ] || [ -f "Pipfile" ]; then
    if command -v pip-audit &>/dev/null; then
        echo "  Running pip-audit..."
        pip-audit --quiet 2>&1 | head -20 || true
    else
        warn "pip-audit not installed (pip install pip-audit)"
        echo "  To check: pip-audit -r requirements.txt"
    fi
fi
if [ -f "package.json" ]; then
    if command -v npm &>/dev/null && [ -f "package-lock.json" ]; then
        echo "  Running npm audit..."
        npm audit --audit-level=high 2>&1 | tail -15 || true
    else
        warn "Cannot audit Node deps (npm/lockfile missing)"
    fi
fi

# ── 7. Docker Security ───────────────────────────────────────────────────────
section "7. Docker Security"
if [ -f "docker-compose.yml" ]; then
    grep -qi "read_only\|read-only" docker-compose.yml 2>/dev/null && pass "Read-only root fs config" || warn "No read-only root fs"
    grep -qi "no-new-privileges\|security_opt" docker-compose.yml 2>/dev/null && pass "no-new-privileges set" || warn "no-new-privileges not set"
    grep -qi "deploy\|resources\|limits\|cpus\|memory" docker-compose.yml 2>/dev/null && pass "Resource limits set" || warn "Resource limits not set"
fi

# ── 8. CORS ──────────────────────────────────────────────────────────────────
section "8. CORS Configuration"
if [ -f "backend/main.py" ]; then
    grep -q 'allow_origins=\["\*"\]' backend/main.py 2>/dev/null && fail "CORS allows all origins (*)" || pass "CORS origins configured"
fi

# ── 9. Security Headers ──────────────────────────────────────────────────────
section "9. Security Headers"
if [ -f "nginx/conf.d/default.conf" ]; then
    for h in "X-Content-Type-Options" "X-Frame-Options" "X-XSS-Protection" "Referrer-Policy" "Content-Security-Policy" "Permissions-Policy"; do
        grep -q "$h" nginx/conf.d/default.conf 2>/dev/null && pass "Header '$h' configured" || warn "Header '$h' missing"
    done
fi

# ── 10. Hardcoded Secrets in Source Code ──────────────────────────────────────
section "10. Hardcoded Secrets"
found=0
for pattern in 'password\s*=\s*["'\''][^"'\'']+["'\'']' 'api_key\s*=\s*["'\''][^"'\'']+["'\'']' 'secret\s*=\s*["'\''][^"'\'']+["'\'']' 'token\s*=\s*["'\''][^"'\'']+["'\'']'; do
    matches=$(grep -rn "$pattern" --include="*.py" --include="*.js" --include="*.ts" --include="*.yml" --include="*.yaml" \
        --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.venv \
        --exclude="*.example" --exclude="*.md" . 2>/dev/null | grep -v "your-\|change-me\|placeholder\|example\|test\|mock\|fake\|\${" | head -10 || true)
    if [ -n "$matches" ]; then
        warn "Possible hardcoded secrets: $pattern"
        echo "$matches" | while read -r line; do echo "    $line"; done
        found=1
    fi
done
[ $found -eq 0 ] && pass "No obvious hardcoded secrets"

# ── Summary ──────────────────────────────────────────────────────────────────
section "Audit Summary"
echo ""
echo "  PASS:  $PASSES"
echo "  WARN:  $WARNINGS"
echo "  FAIL:  $FAILURES"
echo ""
echo "  Report: $REPORT_FILE"
{
    echo "Security Audit - $(date)"; echo "========================================"
    echo "PASS: $PASSES | WARN: $WARNINGS | FAIL: $FAILURES"
    echo "Project: Real-Time Analytics Dashboard"
} > "$REPORT_FILE"

[ $FAILURES -gt 0 ] && { echo -e "${RED}⚠️  $FAILURES failures${NC}"; exit 1; }
[ $WARNINGS -gt 0 ] && { echo -e "${YELLOW}⚠️  $WARNINGS warnings${NC}"; exit 0; }
echo -e "${GREEN}✅ All checks passed${NC}"
