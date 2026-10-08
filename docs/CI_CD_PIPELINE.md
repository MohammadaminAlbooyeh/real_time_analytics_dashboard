# CI/CD Pipeline Documentation

## Overview

This project uses GitHub Actions for continuous integration and continuous deployment. The pipeline is designed to ensure code quality, security, and reliability through automated testing, linting, and deployment processes.

## Pipeline Architecture

### Workflows

```
┌─────────────────────────────────────────────────────────────┐
│                    CI Pipeline (ci.yml)                     │
│              Orchestrates all quality checks                │
└──────────┬──────────────────────┬────────────┬──────────────┘
           │                      │            │
      ┌────▼─────┐         ┌──────▼─────┐  ┌──▼──────┐
      │ Linting  │         │   Tests    │  │Security │
      │(lint.yml)│         │(tests.yml) │  │(sec.yml)│
      └──────────┘         └────────────┘  └─────────┘
           │                      │            │
           └──────────┬───────────┴────────────┘
                      │
                   ┌──▼──────┐
                   │  Build  │
                   │(build.yml)
                   └──────────┘
                      │
              ┌───────┴────────┐
              │                │
         ┌────▼────┐      ┌────▼─────┐
         │ Staging │      │Production│
         │(deploy) │      │(deploy)  │
         └─────────┘      └──────────┘
```

## Workflows

### 1. **Linting** (`lint.yml`)
Validates code style and formatting.

**Triggers:**
- Push to main/develop
- Pull requests

**Jobs:**
- **Python Lint**: Checks Python code with flake8, black, isort
- **JavaScript Lint**: Checks frontend code with ESLint and Prettier
- **Dockerfile Lint**: Validates Dockerfiles with hadolint
- **YAML Lint**: Validates GitHub Actions workflow files

**Pass Criteria:**
- All linting checks must pass
- Code style must conform to project standards

### 2. **Tests** (`tests.yml`)
Runs unit and integration tests.

**Triggers:**
- Push to main/develop
- Pull requests

**Services:**
- PostgreSQL with TimescaleDB
- Redis

**Jobs:**
- **Backend Tests**: Python pytest with 80% coverage threshold
  - Database integration tests
  - API endpoint tests
  - Service layer tests
- **Frontend Tests**: Jest/npm test suite

**Pass Criteria:**
- All tests must pass
- Code coverage ≥ 80%
- No test timeouts

### 3. **Security Scans** (`security.yml`)
Performs comprehensive security analysis.

**Triggers:**
- Push to main/develop
- Pull requests
- Daily schedule (midnight UTC)

**Jobs:**
- **Python Security**: Safety, pip-audit, Bandit checks
- **JavaScript Security**: npm audit
- **Container Security**: Trivy image scanning
- **SAST**: CodeQL analysis
- **Secret Detection**: Gitleaks, TruffleHog
- **Dependency Review**: Only on PRs

**Pass Criteria:**
- No critical vulnerabilities in SAST
- No hardcoded secrets detected
- Container images clean (on demand)

### 4. **Build** (`build.yml`)
Builds and pushes Docker images.

**Triggers:**
- Push to main/develop
- Tags (v*)
- Pull requests (build only, no push)

**Jobs:**
- **Build Backend**: Creates backend Docker image
- **Build Frontend**: Creates frontend Docker image

**Features:**
- Layer caching with GitHub Actions cache
- Multi-registry support (GitHub Container Registry + Docker Hub)
- Semantic versioning support
- Build metadata tagging

**Push Conditions:**
- Always on main/develop branches
- On version tags
- Never on PRs (security measure)

### 5. **Deployment** (`deploy.yml`)
Manages staging and production deployments.

**Triggers:**
- Push to main (staging auto-deploy)
- Manual workflow dispatch
- Version tags (production)

**Environments:**
- **Staging**: Auto-deployed on main branch
  - URL: https://staging-analytics.example.com
  - Health checks included
- **Production**: Manual approval required
  - URL: https://analytics.example.com
  - Smoke tests included
  - Deployment verification steps

### 6. **CI Pipeline** (`ci.yml`)
Orchestrates all quality checks into a unified pipeline.

**Triggers:**
- Push to main/develop
- Pull requests

**Quality Gate:**
- Linting must pass
- Tests must pass
- Build must succeed
- Security issues logged (non-blocking)

## Setup & Configuration

### Secrets Required

Configure these in GitHub repository settings (Settings → Secrets and variables → Actions):

```
DOCKER_USERNAME        # Docker Hub username for image pushes
DOCKER_PASSWORD        # Docker Hub authentication token
GITGUARDIAN_API_KEY    # GitGuardian API key (optional, for secret scanning)
```

### Branch Protection Rules

Recommended settings for `main` branch:

- ✅ Require status checks to pass:
  - `CI Pipeline / Lint`
  - `CI Pipeline / Tests`
  - `CI Pipeline / Build`
- ✅ Require code review
- ✅ Dismiss stale reviews when new commits pushed
- ✅ Allow force pushes: No
- ✅ Allow deletions: No

### Required Status Checks

Enforce these on `main` branch:

1. `lint-results` - All linting passed
2. `test-results` - All tests passed
3. `build-results` - Docker builds succeeded

## Local Development

### Running Linting Locally

```bash
# Python
flake8 backend/ --max-line-length=100
black --check --line-length=100 backend/
isort --check-only --profile=black backend/

# JavaScript
cd frontend && npm run lint

# Dockerfiles
docker run --rm -i hadolint/hadolint < Dockerfile.backend
```

### Running Tests Locally

```bash
# Backend
pytest tests/ -v --cov=backend --cov-report=term-missing

# Frontend
cd frontend && npm test -- --coverage
```

### Running Security Checks Locally

```bash
# Python
pip install safety pip-audit bandit
safety check
pip-audit -r requirements.txt
bandit -r backend/

# JavaScript
npm audit
```

## Monitoring & Troubleshooting

### View Workflow Runs

1. Go to Actions tab in GitHub
2. Select workflow name to filter
3. Click on a run for details
4. Expand failed job to see error logs

### Common Issues

#### Linting Failures

**Issue**: `black --check` fails
```bash
# Fix locally
black backend/
```

**Issue**: `isort` conflicts
```bash
# Fix locally
isort backend/ --profile=black
```

#### Test Failures

**Issue**: Database connection fails
- Ensure PostgreSQL service is running
- Check `DATABASE_URL` environment variable
- Verify Alembic migrations: `alembic upgrade head`

**Issue**: Coverage below 80%
- Add tests for uncovered code paths
- Run locally: `pytest --cov --cov-report=html`

#### Docker Build Failures

**Issue**: `DOCKER_USERNAME` or `DOCKER_PASSWORD` missing
- Add secrets to GitHub repository settings
- Verify token permissions

**Issue**: Build layer cache issues
- Can force rebuild by modifying Dockerfile metadata
- Check GitHub Actions cache usage

#### Security Scan Failures

**Issue**: Vulnerabilities detected
- Review report in GitHub Security tab
- Update vulnerable dependencies
- Add CVE exceptions if necessary (document in SECURITY.md)

### Artifact Retention

- Security reports: 30 days
- Build artifacts: 7 days
- Environment backups: 7 days

## Performance Optimization

### Caching Strategy

- **pip cache**: Enabled via actions/setup-python
- **npm cache**: Enabled via actions/setup-node
- **Docker layer cache**: GitHub Actions cache (mode=max)

### Parallel Execution

- Linting, tests, and security scans run in parallel
- Build waits for tests and linting
- Deployment waits for build completion

### Concurrency

- Only one workflow per branch at a time
- Previous runs cancelled when new push arrives
- Prevents unnecessary resource usage

## Cost Optimization

### GitHub Actions Minutes

The pipeline is optimized for free tier usage:
- Total CI time per run: ~10-15 minutes
- Free tier: 2,000 minutes/month (free accounts)

To monitor:
1. Settings → Billing and plans → Actions

## Security Best Practices

### Implemented

✅ No secrets in workflows
✅ GITHUB_TOKEN has minimal permissions
✅ Docker images never pushed on PRs
✅ Dependency scanning enabled
✅ Secret detection in place
✅ CodeQL SAST enabled
✅ Container image scanning enabled

### Recommendations

- Regularly rotate Docker Hub token
- Review GitHub Actions logs in Security tab
- Keep dependencies updated via Dependabot
- Use branch protection rules
- Enable audit logging for deployments

## Future Enhancements

- [ ] Slack notifications for workflow status
- [ ] Automated rollback on deployment failure
- [ ] Performance benchmarking in CI
- [ ] Database schema migration testing
- [ ] End-to-end test suite
- [ ] Load testing before production deployments
- [ ] Canary deployments
- [ ] Automated changelog generation

## Related Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment procedures
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Developer guidelines
