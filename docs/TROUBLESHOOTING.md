# Troubleshooting Guide

## Common Issues

### Services Won't Start

**Problem**: Docker containers exit immediately

**Solutions**:
1. Check logs: `docker-compose logs backend`
2. Verify .env file exists with required variables
3. Ensure ports are not in use: `lsof -i :8000`
4. Check disk space: `df -h`
5. Rebuild images: `docker-compose build --no-cache`

### Database Connection Error

**Problem**: "Connection refused" or "authentication failed"

**Solutions**:
1. Verify DATABASE_URL in .env
2. Check PostgreSQL is running: `docker-compose ps postgres`
3. Verify credentials match docker-compose.yml
4. Try reconnecting: `docker-compose restart postgres`
5. Check logs: `docker-compose logs postgres`

### Frontend Can't Connect to API

**Problem**: CORS error or connection refused

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check REACT_APP_API_URL in frontend/.env
3. Verify CORS is enabled in backend
4. Check network connectivity between containers
5. Try: `docker-compose logs nginx`

### High Memory Usage

**Problem**: Docker processes consuming excessive RAM

**Solutions**:
1. Check which service: `docker stats`
2. Reduce Redis memory: Adjust maxmemory in redis.conf
3. Tune PostgreSQL shared_buffers
4. Increase swap or add more RAM
5. Limit container memory in docker-compose.yml

### Slow Queries

**Problem**: API responses are slow

**Solutions**:
1. Enable query logging: Set log_min_duration_statement in PostgreSQL
2. Check indexes: `EXPLAIN ANALYZE <query>`
3. Monitor with: `docker-compose logs backend`
4. Review Prometheus metrics on :8001/metrics
5. Check CPU/IO: `docker stats`

### Kafka Issues

**Problem**: Messages not flowing through Kafka

**Solutions**:
1. Verify Kafka is running: `docker-compose ps kafka`
2. Check topic exists:
   ```bash
   docker-compose exec kafka kafka-topics.sh \
     --list --bootstrap-server kafka:29092
   ```
3. Monitor consumer lag
4. Check for broker errors in logs
5. Restart Kafka: `docker-compose restart kafka`

### Redis Connection Issues

**Problem**: "Unable to connect to Redis"

**Solutions**:
1. Verify Redis running: `docker-compose ps redis`
2. Test connection: `docker-compose exec redis redis-cli ping`
3. Check REDIS_URL in .env
4. Clear Redis cache: `docker-compose exec redis redis-cli FLUSHALL`
5. Restart Redis: `docker-compose restart redis`

### Login Issues

**Problem**: Cannot login or invalid credentials

**Solutions**:
1. Verify user exists:
   ```bash
   docker-compose exec postgres psql \
     -U analytics_user -d analytics_db \
     -c "SELECT * FROM users;"
   ```
2. Reset password:
   ```bash
   docker-compose exec backend python scripts/reset_password.py
   ```
3. Create new admin:
   ```bash
   docker-compose exec backend python scripts/create_admin.py
   ```

### JWT Token Issues

**Problem**: "Invalid token" or "Token expired"

**Solutions**:
1. Clear browser storage and cache
2. Verify SECRET_KEY hasn't changed in .env
3. Check token expiration: JWT_EXPIRATION_HOURS in .env
4. Ensure system clock is synchronized
5. Check API logs for token validation errors

### WebSocket Connection Failed

**Problem**: Real-time updates not working

**Solutions**:
1. Verify WebSocket endpoint: ws://localhost:8000/ws
2. Check Nginx WebSocket config
3. Ensure token is valid (same as used for HTTP)
4. Check browser console for errors
5. Monitor: `docker-compose logs backend | grep websocket`

### Database Migration Failed

**Problem**: Alembic migration error

**Solutions**:
1. Check migration status:
   ```bash
   docker-compose exec backend alembic current
   ```
2. View migration history:
   ```bash
   docker-compose exec backend alembic history
   ```
3. Downgrade if needed:
   ```bash
   docker-compose exec backend alembic downgrade -1
   ```
4. Review migration files in database/migrations/
5. Check database logs

### File Upload Issues

**Problem**: Unable to upload files or export data

**Solutions**:
1. Check disk space: `df -h`
2. Verify file permissions: `ls -l data/`
3. Check file size limits in Nginx config
4. Review logs: `docker-compose logs backend`

### Port Already in Use

**Problem**: "Address already in use" error

**Solutions**:
1. Find process using port:
   ```bash
   lsof -i :8000  # For port 8000
   ```
2. Kill process: `kill -9 <PID>`
3. Or change port in docker-compose.yml:
   ```yaml
   ports:
     - "8080:8000"  # Maps to 8080
   ```

## Performance Optimization

### Backend Performance

1. **Enable query caching** in Redis
2. **Use pagination** for large datasets
3. **Add database indexes** for frequently queried columns
4. **Optimize JSON serialization**
5. **Use connection pooling**

### Frontend Performance

1. **Lazy load components**
2. **Code split** route components
3. **Memoize expensive computations**
4. **Use React DevTools Profiler**
5. **Monitor bundle size**

### Database Performance

1. **Add appropriate indexes**
2. **Analyze query plans**
3. **Archive old data**
4. **Tune PostgreSQL parameters**
5. **Monitor with pg_stat_statements**

## Debugging

### Enable Debug Mode

In `.env`:
```
DEBUG=true
LOG_LEVEL=DEBUG
```

### View Detailed Logs

```bash
# Backend logs with full context
docker-compose logs -f --tail=100 backend

# PostgreSQL logs
docker-compose logs -f --tail=100 postgres

# Frontend logs (browser console)
# Open DevTools (F12) and check Console tab
```

### Test API Manually

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin"}' \
  | jq -r '.access_token')

# Test endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/metrics
```

### Database Inspection

```bash
# Connect to database
docker-compose exec postgres psql \
  -U analytics_user -d analytics_db

# Common queries
\dt                    # List tables
SELECT * FROM users;   # View users
SELECT * FROM metrics; # View metrics
```

## Support

If issues persist:

1. Check documentation again
2. Review logs thoroughly
3. Search GitHub issues
4. Create detailed bug report with logs
5. Include system information (OS, versions, etc.)
