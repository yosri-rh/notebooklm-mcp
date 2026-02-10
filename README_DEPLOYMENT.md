# NotebookLM MCP Server - Deployment Guide

Complete guide for deploying NotebookLM MCP Server using Docker and Kubernetes.

## Table of Contents
- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites
- Docker or Kubernetes cluster
- Google account with NotebookLM access
- (Optional) Helm 3.x for Kubernetes deployment

## Docker Deployment

### 1. Build the Image

```bash
# Clone the repository
git clone https://github.com/yourusername/notebooklm-mcp.git
cd notebooklm-mcp

# Build the Docker image
docker build -t notebooklm-mcp:latest .
```

### 2. Run with Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### 3. Run with Docker CLI

```bash
# Create a volume for persistent data
docker volume create notebooklm-chrome-data

# Run the container
docker run -d \
  --name notebooklm-mcp \
  --restart unless-stopped \
  -e NOTEBOOKLM_HEADLESS=true \
  -e LOG_LEVEL=INFO \
  -v notebooklm-chrome-data:/app/chrome-user-data \
  notebooklm-mcp:latest

# View logs
docker logs -f notebooklm-mcp
```

### 4. Authenticate

```bash
# Exec into the container
docker exec -it notebooklm-mcp /bin/bash

# Run authentication setup
uv run python scripts/setup_auth.py
```

### 5. Use Pre-built Image

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/yourusername/notebooklm-mcp:latest

# Run it
docker run -d \
  --name notebooklm-mcp \
  -v notebooklm-chrome-data:/app/chrome-user-data \
  ghcr.io/yourusername/notebooklm-mcp:latest
```

## Kubernetes Deployment

### Using Helm (Recommended)

#### 1. Install the Helm Chart

```bash
# Add the repository (if published to a Helm repo)
# helm repo add notebooklm https://yourusername.github.io/notebooklm-mcp
# helm repo update

# Or install from local chart
helm install notebooklm-mcp ./helm/notebooklm-mcp
```

#### 2. Customize Installation

Create a `values-custom.yaml`:

```yaml
# values-custom.yaml
image:
  repository: ghcr.io/yourusername/notebooklm-mcp
  tag: "v0.1.0"

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

persistence:
  enabled: true
  size: 2Gi
  storageClass: "fast-ssd"

env:
  NOTEBOOKLM_HEADLESS: "true"
  LOG_LEVEL: "DEBUG"

nodeSelector:
  workload: ai-tools
```

Install with custom values:

```bash
helm install notebooklm-mcp ./helm/notebooklm-mcp -f values-custom.yaml
```

#### 3. Upgrade

```bash
# Upgrade with new values
helm upgrade notebooklm-mcp ./helm/notebooklm-mcp -f values-custom.yaml

# Rollback if needed
helm rollback notebooklm-mcp
```

#### 4. Uninstall

```bash
helm uninstall notebooklm-mcp
```

### Using kubectl (Manual Deployment)

#### 1. Create Namespace

```bash
kubectl create namespace notebooklm-mcp
```

#### 2. Create PersistentVolumeClaim

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: notebooklm-chrome-data
  namespace: notebooklm-mcp
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```bash
kubectl apply -f pvc.yaml
```

#### 3. Create ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: notebooklm-config
  namespace: notebooklm-mcp
data:
  NOTEBOOKLM_HEADLESS: "true"
  LOG_LEVEL: "INFO"
```

```bash
kubectl apply -f configmap.yaml
```

#### 4. Create Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notebooklm-mcp
  namespace: notebooklm-mcp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notebooklm-mcp
  template:
    metadata:
      labels:
        app: notebooklm-mcp
    spec:
      containers:
      - name: notebooklm-mcp
        image: ghcr.io/yourusername/notebooklm-mcp:latest
        envFrom:
        - configMapRef:
            name: notebooklm-config
        resources:
          limits:
            cpu: 2000m
            memory: 2Gi
          requests:
            cpu: 500m
            memory: 1Gi
        volumeMounts:
        - name: chrome-data
          mountPath: /app/chrome-user-data
      volumes:
      - name: chrome-data
        persistentVolumeClaim:
          claimName: notebooklm-chrome-data
```

```bash
kubectl apply -f deployment.yaml
```

#### 5. Verify Deployment

```bash
# Check pods
kubectl get pods -n notebooklm-mcp

# View logs
kubectl logs -f deployment/notebooklm-mcp -n notebooklm-mcp

# Describe pod for troubleshooting
kubectl describe pod -l app=notebooklm-mcp -n notebooklm-mcp
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTEBOOKLM_HEADLESS` | `true` | Run browser in headless mode |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Persistent Storage

The Chrome user data (authentication) needs to be persisted:

- **Docker**: Use named volumes or bind mounts
- **Kubernetes**: Use PersistentVolumeClaims (PVC)

Recommended storage sizes:
- Minimum: 500Mi
- Recommended: 1Gi
- For heavy use: 2Gi

## Authentication

### Initial Setup

Authentication must be done once per deployment:

#### Docker

```bash
# Method 1: Exec into container
docker exec -it notebooklm-mcp /bin/bash
uv run python scripts/setup_auth.py

# Method 2: Run with host network for easier auth
docker run -it --rm \
  --network host \
  -e NOTEBOOKLM_HEADLESS=false \
  -v $(pwd)/chrome-user-data:/app/chrome-user-data \
  notebooklm-mcp:latest \
  uv run python scripts/setup_auth.py
```

#### Kubernetes

```bash
# Exec into pod
kubectl exec -it deployment/notebooklm-mcp -n notebooklm-mcp -- /bin/bash

# Run authentication
uv run python scripts/setup_auth.py
```

### Pre-authenticated Volume

For production, consider:

1. Authenticate locally
2. Create PV from authenticated volume
3. Mount in Kubernetes

```bash
# Local authentication
uv run python scripts/setup_auth.py

# Create tarball of chrome-user-data
tar czf chrome-user-data.tar.gz chrome-user-data/

# Copy to cluster node or object storage
# Create PV from this data
```

## Scaling Considerations

### Replicas

- **Recommended**: 1 replica (authentication is per-container)
- **Multiple replicas**: Each needs separate authentication

### Resource Requirements

Minimum:
- CPU: 500m
- Memory: 1Gi

Recommended for production:
- CPU: 1000m-2000m
- Memory: 2Gi

### Storage Performance

- Use SSD-backed storage for better Chromium performance
- Enable read-write-once access mode
- Consider node affinity to keep pod on same node

## Monitoring

### Health Checks

The container includes health checks:

```yaml
livenessProbe:
  exec:
    command:
    - python
    - -c
    - "import sys; sys.exit(0)"
  initialDelaySeconds: 30
  periodSeconds: 30

readinessProbe:
  exec:
    command:
    - python
    - -c
    - "import sys; sys.exit(0)"
  initialDelaySeconds: 15
  periodSeconds: 10
```

### Logging

View logs:

```bash
# Docker
docker logs -f notebooklm-mcp

# Kubernetes
kubectl logs -f deployment/notebooklm-mcp -n notebooklm-mcp

# With Helm
kubectl logs -f -l app.kubernetes.io/name=notebooklm-mcp
```

## Troubleshooting

### Common Issues

#### 1. Authentication Fails

```bash
# Check if chrome-user-data is empty
docker exec notebooklm-mcp ls -la /app/chrome-user-data

# Re-run authentication
docker exec -it notebooklm-mcp uv run python scripts/setup_auth.py
```

#### 2. Container Crashes

```bash
# Check logs
docker logs notebooklm-mcp

# Common causes:
# - Insufficient memory (increase to 2Gi)
# - Missing Chromium dependencies (rebuild image)
# - Permission issues (check volumes)
```

#### 3. Chromium Issues

```bash
# Run with visible browser for debugging
docker run -it --rm \
  -e NOTEBOOKLM_HEADLESS=false \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  notebooklm-mcp:latest
```

#### 4. Kubernetes Pod Pending

```bash
# Check PVC binding
kubectl get pvc -n notebooklm-mcp

# Check events
kubectl get events -n notebooklm-mcp --sort-by='.lastTimestamp'

# Check resource availability
kubectl describe node
```

### Debug Mode

Enable debug logging:

```bash
# Docker
docker run -e LOG_LEVEL=DEBUG notebooklm-mcp:latest

# Kubernetes
kubectl set env deployment/notebooklm-mcp LOG_LEVEL=DEBUG -n notebooklm-mcp
```

## Production Best Practices

1. **Use specific image tags** instead of `latest`
2. **Set resource limits and requests** appropriately
3. **Use PersistentVolumes** for chrome-user-data
4. **Enable monitoring and logging**
5. **Backup authentication data** periodically
6. **Use secrets** for sensitive configuration
7. **Set up alerts** for pod failures
8. **Test authentication renewal** procedures
9. **Document your deployment** process
10. **Plan for updates** and rollbacks

## Support

- GitHub Issues: https://github.com/yourusername/notebooklm-mcp/issues
- Documentation: https://github.com/yourusername/notebooklm-mcp
- Contributing: See CONTRIBUTING.md

## License

MIT License - See LICENSE file for details
