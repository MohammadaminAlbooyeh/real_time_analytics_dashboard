# Setup Guide

## Prerequisites

- Docker and Docker Compose (v20.10+)
- Git
- (Optional) Python 3.11+ for local development
- (Optional) Node.js 18+ for frontend development

## Quick Start with Docker

### 1. Clone Repository
```bash
git clone <repository-url>
cd real-time-analytics-dashboard
```

### 2. Create Environment Files
```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

Update `.env` with your configuration (database credentials, API keys, etc.)

### 3. Start Services
```bash
docker-compose up -d
```

This starts:
- PostgreSQL with TimescaleDB
- Redis
- Kafka & Zookeeper
- FastAPI Backend
- React Frontend
- Nginx Reverse Proxy

### 4. Initialize Database
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/init_db.py
docker-compose exec backend python scripts/create_admin.py
```

### 5. Access Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Nginx**: http://localhost

Default credentials (change in production):
- Email: `admin@example.com`
- Password: `admin`

## Local Development Setup

### Backend

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run database migrations
alembic upgrade head

# Initialize database
python scripts/init_db.py

# Start backend server
uvicorn backend.main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Update REACT_APP_API_URL if backend is not at localhost:8000

# Start development server
npm start
```

Frontend will open at `http://localhost:3000`

## Database Setup

### Using Docker

The database is automatically initialized with docker-compose. To manually run migrations:

```bash
docker-compose exec backend alembic upgrade head
```

### Local Development

```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/analytics_db
alembic upgrade head
```

## Kafka Setup

Kafka is automatically configured in docker-compose. To create topics manually:

```bash
docker-compose exec kafka kafka-topics.sh \
  --create \
  --bootstrap-server localhost:9092 \
  --topic analytics.metrics \
  --partitions 3 \
  --replication-factor 1
```

## Redis Setup

Redis is automatically configured in docker-compose. Verify connection:

```bash
docker-compose exec redis redis-cli ping
# Should return: PONG
```

## Monitoring

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Health Checks

All services have health checks. View status:

```bash
docker-compose ps
```

### Prometheus Metrics

Access metrics at: `http://localhost:8001/metrics`

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If ports are already in use, modify docker-compose.yml:

```yaml
ports:
  - "8080:8000"  # Maps to 8080 instead of 8000
```

### Database Connection Issues

1. Verify PostgreSQL is running:
   ```bash
   docker-compose logs postgres
   ```

2. Check credentials in .env

3. Restart database service:
   ```bash
   docker-compose restart postgres
   ```

### Frontend Can't Connect to Backend

1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check REACT_APP_API_URL in frontend/.env

3. Verify CORS settings in backend config

## Next Steps

1. Review [API Documentation](API_DOCUMENTATION.md)
2. Check [Architecture](ARCHITECTURE.md)
3. See [Deployment Guide](DEPLOYMENT.md)
4. Read [Contributing Guide](CONTRIBUTING.md)
