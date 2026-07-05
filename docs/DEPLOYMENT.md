# Deployment Guide

## Pre-Deployment Checklist

- [ ] All tests pass
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] SSL certificates prepared
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Security review completed

## Production Deployment

### 1. Prepare Environment

```bash
# Create production .env file
cp .env.example .env.production
# Edit .env.production with production values
```

Key settings for production:
- `APP_ENV=production`
- `DEBUG=false`
- `SECRET_KEY=<strong-random-key>`
- `DATABASE_URL=<production-db-url>`
- `REDIS_URL=<production-redis-url>`
- Disable CORS * origins

### 2. Build Docker Images

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

### 3. Database Migration

```bash
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

### 4. Deploy Stack

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 5. Verify Deployment

```bash
# Check services are running
docker-compose ps

# Test health endpoints
curl http://your-domain/health
curl http://your-domain:8000/health

# Check logs
docker-compose logs -f backend
```

## Cloud Deployment Options

### AWS ECS

1. Push images to ECR
2. Create ECS task definitions
3. Create ECS service
4. Configure load balancer
5. Set up auto-scaling

### Kubernetes

```yaml
# Example Kubernetes deployment structure
k8s/
  ├── backend-deployment.yaml
  ├── frontend-deployment.yaml
  ├── postgres-statefulset.yaml
  ├── redis-deployment.yaml
  ├── kafka-statefulset.yaml
  ├── nginx-configmap.yaml
  ├── services.yaml
  └── ingress.yaml
```

Deploy with:
```bash
kubectl apply -f k8s/
```

### Heroku

1. Set environment variables
2. Configure Procfile
3. Deploy via Git push

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly -d your-domain.com

# Configure Nginx
# Copy certificate paths to nginx.conf

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Docker SSL Setup

Mount certificates:
```yaml
volumes:
  - /etc/letsencrypt/live/your-domain.com:/etc/nginx/certs:ro
```

## Database Backup

### Automated Backup

```bash
# Create backup script
scripts/backup_db.sh

# Schedule with cron
0 2 * * * /path/to/backup_db.sh
```

### Manual Backup

```bash
docker-compose exec postgres pg_dump \
  -U analytics_user \
  analytics_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore from Backup

```bash
docker-compose exec -T postgres psql \
  -U analytics_user \
  analytics_db < backup_file.sql
```

## Monitoring & Alerts

### Prometheus Setup

Add Prometheus service to docker-compose.yml:
```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"
```

### Grafana Dashboards

1. Access Grafana at http://your-domain:3000
2. Add Prometheus data source
3. Import dashboards from monitoring/dashboards/

### Alert Rules

Configure alert rules in `monitoring/alert_rules.yml`:
```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
```

## Scaling

### Horizontal Scaling

1. **Backend**: Run multiple instances behind load balancer
2. **Database**: Use replication for read scaling
3. **Redis**: Use Redis Cluster
4. **Kafka**: Add brokers as needed

### Performance Tuning

- PostgreSQL: Tune shared_buffers, work_mem
- Redis: Tune maxmemory policy
- Kafka: Adjust num_partitions, replication_factor
- Backend: Tune worker count and timeouts

## Rollback Procedure

```bash
# Tag current version
docker-compose -f docker-compose.prod.yml down

# Use previous image tag
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose logs -f backend
```

## Post-Deployment

1. Run smoke tests
2. Monitor error logs
3. Check performance metrics
4. Validate all features work
5. Update documentation

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs backend

# Verify environment
docker-compose config

# Check dependencies
docker-compose ps
```

### Database Migration Failed

```bash
# View current revision
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

# Downgrade if needed
docker-compose exec backend alembic downgrade -1
```

### Performance Issues

1. Check database query performance
2. Monitor CPU/memory usage
3. Review slow query logs
4. Analyze Prometheus metrics

## Security Best Practices

- Enable HTTPS/TLS
- Use strong database passwords
- Rotate JWT secrets regularly
- Enable database encryption at rest
- Use VPC/private networks
- Implement rate limiting
- Set up Web Application Firewall
- Regular security audits
- Keep dependencies updated
