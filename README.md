# Real-Time Analytics Dashboard

A comprehensive real-time analytics dashboard built with modern web technologies for monitoring metrics, analyzing trends, and triggering alerts.

## Features

- **Real-Time Metrics**: Track and visualize metrics in real-time using WebSocket connections
- **Time-Series Data**: Optimized storage for time-series data using PostgreSQL + TimescaleDB
- **Advanced Analytics**: Statistical analysis, period comparison, and trend detection
- **Alert System**: Create custom alert rules with email/Slack notifications
- **Dashboard Management**: Create and customize dashboards with various chart types
- **Data Export**: Export metric data in CSV/JSON formats
- **Authentication**: Secure JWT-based authentication
- **Multiple Data Sources**: Integrate metrics from HTTP, database, and custom sources
- **Responsive UI**: Modern React-based responsive interface

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL + TimescaleDB
- **Cache**: Redis
- **Message Queue**: Kafka
- **Authentication**: JWT + bcrypt
- **API Documentation**: Swagger/OpenAPI

### Frontend
- **Framework**: React 18
- **State Management**: Redux
- **UI Library**: Tailwind CSS
- **Charts**: Recharts
- **Routing**: React Router v6

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus
- **Message Queue**: Kafka + Zookeeper

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     React Frontend (Port 3000)                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │  │
│  │  │   Pages      │  │  Components  │  │   Redux Store            │  │  │
│  │  │ • Dashboard  │  │ • Header     │  │  • dashboardReducer      │  │  │
│  │  │ • Analytics  │  │ • Sidebar    │  │  • userReducer           │  │  │
│  │  │ • Alerts     │  │ • Charts     │  │  • alertReducer          │  │  │
│  │  │ • Metrics    │  │ • Forms      │  └──────────────────────────┘  │  │
│  │  └──────────────┘  └──────────────┘                                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                               │
│                    ┌─────────┴──────────┐                                   │
│            HTTP/REST (API Calls)    WebSocket (Real-time)                   │
└────────────┼──────────────────────────┼──────────────────────────────────────┘
             │                          │
┌────────────▼──────────────────────────▼──────────────────────────────────────┐
│                        REVERSE PROXY LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│              ┌─────────────────────────────────────────────────┐            │
│              │   Nginx (Port 80, 443)                          │            │
│              │  • Route /api → Backend                         │            │
│              │  • Route / → Frontend                           │            │
│              │  • WebSocket upgrade support                    │            │
│              │  • Gzip compression                             │            │
│              │  • Load balancing                               │            │
│              └─────────────────────────────────────────────────┘            │
│                              │                                               │
└──────────────┬───────────────┼───────────────────────────────────────────────┘
               │               │
    ┌──────────▼──┐   ┌────────▼──────────┐
    │  Backend    │   │  Frontend         │
    │  (8000)     │   │  (3000)           │
    └──────────┬──┘   └───────────────────┘
               │
┌──────────────▼─────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   FastAPI Backend (Port 8000)                       │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │   │
│  │  │  API Routes  │  │  Services    │  │  WebSocket Manager       │ │   │
│  │  │ • /auth      │  │ • Metric     │  │ • Connections           │ │   │
│  │  │ • /metrics   │  │ • Analytics  │  │ • Broadcasting          │ │   │
│  │  │ • /analytics │  │ • Dashboard  │  │ • Event handling        │ │   │
│  │  │ • /dashboards│  │ • Alert      │  │                         │ │   │
│  │  │ • /alerts    │  │ • Datasource │  └──────────────────────────┘ │   │
│  │  │ • /datasource│  │ • Export     │                               │   │
│  │  │ • /reports   │  │ • Cache      │  ┌──────────────────────────┐ │   │
│  │  │ • /export    │  │ • User       │  │  Kafka Producer/Consumer │ │   │
│  │  └──────────────┘  └──────────────┘  │ • Metrics topic          │ │   │
│  │                                       │ • Events topic           │ │   │
│  │  ┌──────────────────────────────────┐ │ • Alerts topic          │ │   │
│  │  │   Notifications System           │ └──────────────────────────┘ │   │
│  │  │ • Email (SendGrid)               │                             │   │
│  │  │ • Slack integration              │  ┌──────────────────────────┐ │   │
│  │  │ • Webhook support                │  │  Authentication          │ │   │
│  │  └──────────────────────────────────┘  │ • JWT token validation   │ │   │
│  │                                        │ • bcrypt password hash   │ │   │
│  │                                        │ • User permissions       │ │   │
│  │                                        └──────────────────────────┘ │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                               │
│                   ┌──────────┼────────────┐                                │
│                   │          │            │                                │
└───────────────────┼──────────┼────────────┼────────────────────────────────┘
                    │          │            │
        ┌───────────▼─┐  ┌────▼──────┐  ┌─▼─────────┐
        │  PostgreSQL │  │   Redis   │  │  Kafka +  │
        │ TimescaleDB │  │  Cache    │  │ Zookeeper │
        │ (5432)      │  │  (6379)   │  │ (9092)    │
        └─────────────┘  └───────────┘  └───────────┘
```

### Data Flow

```
┌─────────────────┐
│  User Input     │
│  (Frontend)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  API Endpoint (Backend)         │
│  ✓ Validate request             │
│  ✓ Authenticate user            │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Business Logic (Services)      │
│  ✓ Process data                 │
│  ✓ Apply rules                  │
└────────┬────────────────────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
    ┌─────────────┐              ┌──────────────────┐
    │  Database   │              │  Message Queue   │
    │ PostgreSQL  │              │  (Kafka)         │
    │ TimescaleDB │              │                  │
    └──────┬──────┘              └────────┬─────────┘
           │                              │
           └──────────────┬───────────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
              ▼           ▼           ▼
         ┌────────┐  ┌────────┐  ┌──────────┐
         │ Cache  │  │Analytics   │WebSocket │
         │(Redis) │  │Engine  │  │Broadcast │
         └────────┘  └────────┘  └──────────┘
              │           │           │
              └───────────┼───────────┘
                          │
                          ▼
                    ┌──────────────┐
                    │  Frontend    │
                    │  Real-time   │
                    │  Update      │
                    └──────────────┘
```

### Component Interactions

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Frontend    │         │  Backend     │         │  Database    │
│  (React)     │         │  (FastAPI)   │         │  (PostgreSQL)│
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │  1. Login              │                        │
       ├───────────────────────►│                        │
       │                        │  2. Verify Creds      │
       │                        ├───────────────────────►│
       │                        │◄───────────────────────┤
       
       │◄───────────────────────┤  3. Return User       │
       │  JWT Token             │                        │
       │                        │                        │
       │  4. Record Metric      │                        │
       ├───────────────────────►│                        │
       │                        │  5. Store Data        │
       │                        ├───────────────────────►│
       │                        │◄───────────────────────┤
       │                        │  6. Confirm           │
       │◄───────────────────────┤                        │
       │                        │                        │
       │                        │  7. Publish to Kafka  │
       │                        ├────────────────────┐  │
       │                        │                    │  │
       │  8. WebSocket Update   │  9. Process/Cache  │  │
       │◄───────────────────────┤                    │  │
       │  Real-time            │                    ▼  │
       │                        │              ┌─────────┐
       │                        │              │ Kafka   │
       │                        │              │ Topic   │
       │                        │              └─────────┘
       │                        │
```

## Quick Start

### Using Docker Compose

```bash
# Clone repository
git clone <repo-url>
cd real-time-analytics-dashboard

# Create environment files
cp .env.example .env
cp frontend/.env.example frontend/.env

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/init_db.py

# Access application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

See [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed local development setup.

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - System design and components
- [API Documentation](docs/API_DOCUMENTATION.md) - Endpoint reference
- [Setup Guide](docs/SETUP_GUIDE.md) - Installation and configuration
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [Data Pipeline](docs/DATA_PIPELINE.md) - Data flow and processing
- [Alert Rules](docs/ALERT_RULES.md) - Alert configuration
- [Kafka Configuration](docs/KAFKA_CONFIG.md) - Message queue setup
- [Metric Definitions](docs/METRIC_DEFINITIONS.md) - Metric creation guide
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Contributing Guide](docs/CONTRIBUTING.md) - Development guidelines

## Project Structure

```
├── backend/                 # FastAPI application
│   ├── api/                # API routes and schemas
│   ├── models/             # Database models
│   ├── services/           # Business logic
│   ├── kafka/              # Kafka producer/consumer
│   ├── websocket/          # WebSocket handlers
│   └── notifications/      # Email, Slack, Webhook
├── frontend/               # React application
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── charts/        # Chart components
│   │   ├── store/         # Redux store
│   │   └── utils/         # Utilities
├── database/              # Alembic migrations
├── config/               # Configuration files
├── scripts/              # Utility scripts
├── tests/                # Test suite
├── docs/                 # Documentation
├── nginx/                # Nginx configuration
├── monitoring/           # Prometheus setup
└── docker-compose.yml    # Service orchestration
```

## API Overview

### Key Endpoints

- `POST /api/auth/login` - User login
- `POST /api/v1/metrics` - Create metric
- `POST /api/v1/metrics/{id}/data` - Record metric data
- `GET /api/v1/analytics/timeseries` - Get time-series data
- `GET /api/v1/analytics/summary/{id}` - Get metric summary
- `POST /api/v1/dashboards` - Create dashboard
- `POST /api/v1/alerts/rules` - Create alert rule
- `WS /ws` - WebSocket for real-time updates

See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for complete reference.

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_metrics.py -v
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feedback:
- Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Review [FAQ](docs/FAQ.md)
- Open a GitHub issue
- Contact the development team

## Roadmap

- [x] GraphQL API
- [x] Data retention policies
- [x] Advanced anomaly detection (Isolation Forest)
- [x] Custom webhook templating (Jinja2)
- [x] SAML/OAuth authentication
- [x] Multi-tenant support
- [x] Data encryption at rest (AES-256-GCM)
- [x] Compliance reports (GDPR, SOC2)
- [x] Machine Learning predictions (Random Forest)
- [x] Rate limiting (slowapi)
- [x] HTTPS/TLS support (Nginx + Let's Encrypt ready)

## Status

| Component | Status |
|-----------|--------|
| Backend | ✅ Complete |
| Frontend | ✅ Complete |
| Docker Setup | ✅ Complete |
| Tests | ✅ Complete |
| Documentation | ✅ Complete |
| CI/CD Pipeline | ✅ Complete |
| Deployment Ready | ✅ Ready |
