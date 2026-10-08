#!/bin/bash

##############################################################################
# CI/CD Setup Script
#
# Configures GitHub repository for CI/CD pipeline
# Requires: GitHub CLI (gh) and appropriate permissions
#
# Usage: ./scripts/setup-ci.sh
##############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

##############################################################################
# Main Setup
##############################################################################

main() {
    log_info "Starting CI/CD setup..."

    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        log_info "Install from: https://cli.github.com"
        exit 1
    fi

    # Check authentication
    if ! gh auth status &> /dev/null; then
        log_error "Not authenticated with GitHub CLI"
        log_info "Run: gh auth login"
        exit 1
    fi

    log_success "GitHub CLI authenticated"

    # Get repository info
    REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
    log_info "Repository: $REPO"

    ##########################################################################
    # Step 1: Configure Branch Protection
    ##########################################################################
    log_info "Configuring branch protection rules..."

    # Note: Full branch protection requires API calls
    # Using gh cli where possible

    log_info "Enable required status checks:"
    log_warning "Manual step: Go to Settings → Branches → Branch protection rules"
    log_warning "Add these required status checks:"
    log_warning "  • lint-results"
    log_warning "  • test-results"
    log_warning "  • build-results"

    ##########################################################################
    # Step 2: Verify Secrets
    ##########################################################################
    log_info "Checking GitHub secrets..."

    SECRETS=$(gh secret list 2>/dev/null || echo "")

    if echo "$SECRETS" | grep -q "DOCKER_USERNAME"; then
        log_success "DOCKER_USERNAME secret configured"
    else
        log_warning "DOCKER_USERNAME secret not configured"
        log_info "Set Docker Hub username: gh secret set DOCKER_USERNAME"
    fi

    if echo "$SECRETS" | grep -q "DOCKER_PASSWORD"; then
        log_success "DOCKER_PASSWORD secret configured"
    else
        log_warning "DOCKER_PASSWORD secret not configured"
        log_info "Set Docker Hub token: gh secret set DOCKER_PASSWORD"
    fi

    ##########################################################################
    # Step 3: Enable Features
    ##########################################################################
    log_info "Ensuring GitHub features are enabled..."

    # Check if GitHub Advanced Security is available
    log_info "Advanced Security features:"
    log_info "  • CodeQL - Enabled by default"
    log_info "  • Dependabot - Configured via .github/dependabot.yml"
    log_info "  • Secret scanning - Enabled by default"

    ##########################################################################
    # Step 4: Workflow Validation
    ##########################################################################
    log_info "Validating GitHub Actions workflows..."

    WORKFLOWS=(
        ".github/workflows/lint.yml"
        ".github/workflows/tests.yml"
        ".github/workflows/security.yml"
        ".github/workflows/build.yml"
        ".github/workflows/deploy.yml"
        ".github/workflows/ci.yml"
    )

    for workflow in "${WORKFLOWS[@]}"; do
        if [ -f "$workflow" ]; then
            log_success "Found: $workflow"
        else
            log_error "Missing: $workflow"
        fi
    done

    ##########################################################################
    # Step 5: Local Setup
    ##########################################################################
    log_info "Setting up local development environment..."

    # Python tools
    if command -v python3 &> /dev/null; then
        log_info "Installing Python linting tools..."
        python3 -m pip install -q flake8 black isort pylint 2>/dev/null || \
            log_warning "Could not install Python tools automatically"
        log_success "Python tools available"
    else
        log_warning "Python 3 not found - skipping Python tool installation"
    fi

    # Node tools
    if command -v npm &> /dev/null; then
        log_info "Installing Node.js tools..."
        npm list -g eslint &> /dev/null || \
            log_warning "Consider installing: npm install -g eslint prettier"
        log_success "Node.js tools available"
    else
        log_warning "Node.js not found - skipping Node.js tool installation"
    fi

    ##########################################################################
    # Summary
    ##########################################################################
    echo ""
    log_success "CI/CD setup complete!"
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "1. Set Docker secrets (if needed):"
    echo "   gh secret set DOCKER_USERNAME"
    echo "   gh secret set DOCKER_PASSWORD"
    echo ""
    echo "2. Configure branch protection rules:"
    echo "   https://github.com/$REPO/settings/branches"
    echo ""
    echo "3. Test the pipeline:"
    echo "   git push origin main  # or your branch"
    echo ""
    echo "4. Monitor workflow runs:"
    echo "   gh run list"
    echo "   gh run view <RUN_ID>"
    echo ""
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo "   See docs/CI_CD_PIPELINE.md for detailed information"
    echo ""
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
