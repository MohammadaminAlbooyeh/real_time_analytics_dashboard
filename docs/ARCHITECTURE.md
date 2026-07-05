# Architecture Overview

## System Design

The Real-Time Analytics Dashboard is built on a modern microservices architecture with real-time data processing capabilities.

```
┌─────────────────┐         ┌──────────────────┐
│   React UI      │◄───────►│  FastAPI Backend │
│  (Frontend)     │         │   (REST + WS)    │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         │ HTTP/WebSocket            │
         │                           │
         └───────────┬───────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌───▼────┐  ┌───▼────┐
   │PostgreSQL│  │ Redis  │  │ Kafka  │
   │TimescaleDB  │Cache   │  │Streaming
   └─────────┘  └────────┘  └────────┘
```

## Key Components

### 1. Frontend (React + Redux)
- **Framework**: React 18 with React Router for SPA navigation
- **State Management**: Redux with actions, reducers, and selectors
- **UI Library**: Tailwind CSS + Recharts for visualizations
- **WebSocket**: Real-time updates via WebSocket connections
- **Pages**: Dashboard, Analytics, Alerts, Metrics, Reports, DataSources, Settings

### 2. Backend (FastAPI)
- **Framework**: FastAPI with async/await support
- **Database ORM**: SQLAlchemy 2.0 with async driver (asyncpg)
- **Authentication**: JWT-based with bcrypt password hashing
- **API Routes**: RESTful endpoints for all resources
- **WebSocket**: Real-time data streaming
- **Middleware**: CORS, authentication, error handling

### 3. Data Storage
- **PostgreSQL + TimescaleDB**: Time-series data optimized for analytics
- **Redis**: Caching layer for frequently accessed data
- **Kafka**: Event streaming for real-time data processing

### 4. Services Layer

#### MetricService
- CRUD operations for metric definitions
- Data point recording with timestamps
- Metric aggregation and rollup

#### AnalyticsService
- Time-series data retrieval
- Statistical analysis (min, max, avg, stddev)
- Period comparison
- Trend analysis

#### DashboardService
- Dashboard creation and management
- Widget/item management
- Layout persistence

#### AlertService
- Alert rule creation and management
- Alert event monitoring
- Alert status tracking
- Notification triggering

#### DataSourceService
- External data source integration
- Connection management
- Data polling/webhooks

#### ExportService
- Data export to CSV/JSON
- Report generation
- Scheduled exports

#### NotificationService
- Email notifications (SendGrid)
- Slack notifications
- Webhook notifications

### 5. Message Queue (Kafka)
- **Topics**:
  - `analytics.metrics`: Raw metric data points
  - `analytics.events`: System events
  - `analytics.alerts`: Alert notifications

### 6. Real-time Communication
- **WebSocket Manager**: Handles client connections and broadcasting
- **WebSocket Events**: Metric updates, alert notifications, system events
- **Broadcasting**: Selective message delivery to connected clients

## Data Flow

### Metric Recording Flow
1. Frontend/API sends metric data point
2. Backend stores in PostgreSQL/TimescaleDB
3. Kafka producer publishes to `analytics.metrics` topic
4. Kafka consumer processes for aggregation
5. WebSocket broadcasts real-time update to connected clients
6. Redis caches recent values for fast retrieval

### Alert Processing Flow
1. Alert rule is defined with condition/threshold
2. Analytics engine continuously evaluates conditions
3. When triggered, alert event is created
4. Notification system sends alerts via email/Slack/webhook
5. Alert status is persisted
6. WebSocket notifies connected clients in real-time

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18, Redux, Recharts | UI and state management |
| Backend | FastAPI, Python 3.11 | API and business logic |
| Database | PostgreSQL 15 + TimescaleDB | Time-series data storage |
| Cache | Redis 7 | Session and data caching |
| Messaging | Kafka 7.5 | Event streaming |
| Authentication | JWT + bcrypt | Security |
| Containerization | Docker, Docker Compose | Deployment |
| Reverse Proxy | Nginx | Load balancing |
| Monitoring | Prometheus | Metrics collection |

## Deployment Architecture

### Docker Services
- **postgres**: TimescaleDB for time-series data
- **redis**: In-memory caching
- **zookeeper**: Kafka coordination
- **kafka**: Event streaming broker
- **backend**: FastAPI application
- **frontend**: React application (served by Nginx)
- **nginx**: Reverse proxy and load balancer

### Port Mappings
- Frontend: 3000
- Backend: 8000
- Prometheus: 8001
- PostgreSQL: 5432
- Redis: 6379
- Kafka: 9092
- Nginx: 80, 443

## Security Considerations

1. **Authentication**: JWT tokens with expiration
2. **Authorization**: User-level access control via dependencies
3. **Password Hashing**: bcrypt with salt
4. **CORS**: Configured for allowed origins
5. **Database**: Credentials via environment variables
6. **Secret Key**: Configured via environment

## Scaling Considerations

### Horizontal Scaling
- Stateless backend allows multiple instances
- Load balancing via Nginx
- Database replicas for read scaling
- Redis cluster for cache scaling

### Vertical Scaling
- AsyncIO for concurrent request handling
- Connection pooling for database
- Kafka partition scaling for throughput
- Redis memory optimization

## Monitoring & Observability

- **Prometheus Metrics**: Application metrics exposure
- **Structured Logging**: JSON logging with context
- **Health Checks**: Docker healthchecks
- **Error Tracking**: Exception logging and reporting
