# Kubernetes Deployment

## Prerequisites

- Kubernetes cluster (v1.25+)
- kubectl configured
- cert-manager installed (for TLS)

## Quick Start

```bash
# Apply all resources
kubectl apply -k k8s/

# Verify
kubectl get all -n analytics
kubectl get pvc -n analytics

# Check pod status
kubectl get pods -n analytics -w
```

## Configuration

1. **Secrets**: Edit `k8s/secrets.yaml` with your production values or use SealedSecrets/External Secrets Operator.

2. **Ingress**: Update `k8s/ingress.yaml` with your domain in `spec.rules[0].host` and `spec.tls[0].hosts`.

3. **ConfigMap**: Review `k8s/configmap.yaml` for environment-specific settings.

4. **Resource Limits**: Adjust CPU/memory requests and limits based on your workload.

5. **Storage**: Update storage class and size in PVCs to match your cluster.

## Applying Manifests

```bash
# Apply namespace first
kubectl apply -f k8s/namespace.yaml

# Apply secrets
kubectl apply -f k8s/secrets.yaml

# Apply all resources
kubectl apply -f k8s/
```

## Scaling

The backend, frontend, and nginx deployments have HorizontalPodAutoscalers configured:

- Backend: 2-10 replicas, CPU 70%, Memory 80%
- Frontend: 2-8 replicas, CPU 70%
- Nginx: 2-6 replicas, CPU 70%

Adjust these values in the respective yaml files.

## Rolling Updates

All deployments use RollingUpdate strategy. To trigger an update:

```bash
kubectl set image deployment/backend -n analytics backend=your-registry/analytics-backend:v2
```

## Database Migration

Run Alembic migrations after deployment:

```bash
kubectl exec -n analytics deployment/backend -- alembic upgrade head
```

## Monitoring

- Prometheus metrics available on backend port 8001
- Nginx metrics available via the stub_status module
- Use Prometheus Operator ServiceMonitors to scrape metrics

## Backup

```bash
# Backup PostgreSQL
kubectl exec -n analytics statefulset/postgres -- pg_dump -U analytics_user analytics > backup.sql

# Backup Redis
kubectl exec -n analytics deployment/redis -- redis-cli SAVE
```
