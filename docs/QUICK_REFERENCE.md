# NotebookLM MCP - Quick Reference

Fast command reference for common tasks.

## Podman Commands

### Build & Run

```bash
# Build image
podman build -t notebooklm-mcp:latest .

# Run with Docker Compose
podman-compose up -d

# Run standalone
podman run -d --name notebooklm-mcp \
  -v notebooklm-data:/app/chrome-user-data \
  notebooklm-mcp:latest

# Stop
podman-compose down
# or
podman stop notebooklm-mcp
```

### Manage

```bash
# View logs
podman logs -f notebooklm-mcp

# Exec into container
podman exec -it notebooklm-mcp /bin/bash

# Authenticate
podman exec -it notebooklm-mcp uv run python scripts/setup_auth.py

# Restart
podman restart notebooklm-mcp

# Remove
podman rm -f notebooklm-mcp
```

## Kubernetes Commands

### Deploy with Helm

```bash
# Install
helm install notebooklm-mcp ./helm/notebooklm-mcp

# Install with custom values
helm install notebooklm-mcp ./helm/notebooklm-mcp -f my-values.yaml

# Upgrade
helm upgrade notebooklm-mcp ./helm/notebooklm-mcp

# Uninstall
helm uninstall notebooklm-mcp

# List releases
helm list

# Get values
helm get values notebooklm-mcp
```

### Manage Pods

```bash
# Get pods
kubectl get pods -l app.kubernetes.io/name=notebooklm-mcp

# Describe pod
kubectl describe pod -l app.kubernetes.io/name=notebooklm-mcp

# View logs
kubectl logs -f deployment/notebooklm-mcp

# Exec into pod
kubectl exec -it deployment/notebooklm-mcp -- /bin/bash

# Authenticate
kubectl exec -it deployment/notebooklm-mcp -- uv run python scripts/setup_auth.py

# Delete pod (will recreate)
kubectl delete pod -l app.kubernetes.io/name=notebooklm-mcp
```

### Check Resources

```bash
# Get all resources
kubectl get all -l app.kubernetes.io/name=notebooklm-mcp

# Check PVC
kubectl get pvc

# Check ConfigMap
kubectl get configmap

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Resource usage
kubectl top pod -l app.kubernetes.io/name=notebooklm-mcp
```

## Helm Chart Development

```bash
# Lint chart
helm lint helm/notebooklm-mcp

# Dry run
helm install test helm/notebooklm-mcp --dry-run --debug

# Template (see YAML output)
helm template test helm/notebooklm-mcp

# Template with custom values
helm template test helm/notebooklm-mcp -f values-dev.yaml

# Package chart
helm package helm/notebooklm-mcp

# Show chart values
helm show values helm/notebooklm-mcp

# Show chart info
helm show chart helm/notebooklm-mcp
```

## Local Development

```bash
# Install dependencies
uv sync

# Install Playwright
uv run playwright install chromium

# Authenticate
uv run python scripts/setup_auth.py

# Run server
uv run notebooklm-mcp

# Run with visible browser
NOTEBOOKLM_HEADLESS=false uv run notebooklm-mcp

# Debug mode
LOG_LEVEL=DEBUG uv run notebooklm-mcp

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv --directory . run notebooklm-mcp
```

## Git & GitHub

```bash
# Initialize
git init
git add .
git commit -m "Initial commit"

# Add remote
git remote add origin https://github.com/username/notebooklm-mcp.git

# Push
git push -u origin main

# Create release tag
git tag v0.1.0
git push origin v0.1.0

# Check status
git status

# View branches
git branch -a
```

## CI/CD

```bash
# Manually trigger workflow (GitHub CLI)
gh workflow run docker-publish.yml

# View workflow runs
gh run list

# Watch latest run
gh run watch

# View logs
gh run view --log
```

## Troubleshooting

```bash
# Check Docker logs
podman logs notebooklm-mcp --tail 100

# Check Kubernetes events
kubectl get events --sort-by='.lastTimestamp' | grep notebooklm

# Describe pod for issues
kubectl describe pod -l app.kubernetes.io/name=notebooklm-mcp

# Check PVC binding
kubectl get pvc

# Port forward for testing
kubectl port-forward deployment/notebooklm-mcp 8080:8080

# Check resource usage
podman stats notebooklm-mcp
# or
kubectl top pod -l app.kubernetes.io/name=notebooklm-mcp

# Restart pod
kubectl rollout restart deployment/notebooklm-mcp
```

## Image Management

```bash
# Pull from registry
podman pull ghcr.io/username/notebooklm-mcp:latest

# Tag image
podman tag notebooklm-mcp:latest ghcr.io/username/notebooklm-mcp:v1.0.0

# Push to registry
podman push ghcr.io/username/notebooklm-mcp:v1.0.0

# List local images
podman images | grep notebooklm

# Remove image
podman rmi notebooklm-mcp:latest

# Prune unused images
podman image prune -a
```

## Volume Management

```bash
# List volumes
podman volume ls

# Inspect volume
podman volume inspect notebooklm-chrome-data

# Create volume
podman volume create notebooklm-chrome-data

# Remove volume
podman volume rm notebooklm-chrome-data

# Backup volume
podman run --rm \
  -v notebooklm-chrome-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/chrome-data-backup.tar.gz /data

# Restore volume
podman run --rm \
  -v notebooklm-chrome-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/chrome-data-backup.tar.gz -C /
```

## Monitoring

```bash
# Docker stats
podman stats notebooklm-mcp

# Kubernetes metrics
kubectl top pod -l app.kubernetes.io/name=notebooklm-mcp
kubectl top node

# Stream logs
podman logs -f notebooklm-mcp
# or
kubectl logs -f deployment/notebooklm-mcp --tail=100

# Check health
podman inspect --format='{{.State.Health.Status}}' notebooklm-mcp
```

## Quick Debugging

```bash
# Run container interactively
podman run -it --rm notebooklm-mcp:latest /bin/bash

# Check if Chromium works
podman run --rm notebooklm-mcp:latest uv run playwright --version

# Test Python imports
podman run --rm notebooklm-mcp:latest \
  uv run python -c "from src.notebooklm_mcp import server; print('OK')"

# Check environment
podman run --rm notebooklm-mcp:latest env | grep NOTEBOOKLM
```

## Cleanup

```bash
# Stop and remove everything (Docker)
podman-compose down -v

# Remove Helm release and PVC
helm uninstall notebooklm-mcp
kubectl delete pvc -l app.kubernetes.io/name=notebooklm-mcp

# Prune Docker system
podman system prune -a --volumes

# Delete namespace (K8s)
kubectl delete namespace notebooklm-mcp
```

## Environment Variables

```bash
# Docker
podman run -e NOTEBOOKLM_HEADLESS=false \
  -e LOG_LEVEL=DEBUG \
  notebooklm-mcp:latest

# Kubernetes
kubectl set env deployment/notebooklm-mcp LOG_LEVEL=DEBUG

# Docker Compose (in .env file)
echo "NOTEBOOKLM_HEADLESS=true" > .env
echo "LOG_LEVEL=INFO" >> .env
```

## Common Issues & Fixes

```bash
# Issue: Authentication expired
podman exec -it notebooklm-mcp uv run python scripts/setup_auth.py

# Issue: Pod crash loop
kubectl describe pod -l app.kubernetes.io/name=notebooklm-mcp
kubectl logs -f deployment/notebooklm-mcp --previous

# Issue: PVC not binding
kubectl get pvc
kubectl describe pvc notebooklm-mcp

# Issue: Image pull errors
kubectl describe pod -l app.kubernetes.io/name=notebooklm-mcp | grep -A 5 Events

# Issue: Out of memory
# Increase memory limit in values.yaml or podman-compose.yml
resources:
  limits:
    memory: 4Gi  # Increase from 2Gi
```

---

## Cheat Sheet URLs

- Podman Docs: https://docs.podman.io
- Kubernetes Docs: https://kubernetes.io/docs
- Helm Docs: https://helm.sh/docs
- GitHub Actions: https://docs.github.com/en/actions
- Playwright Docs: https://playwright.dev

---

**Save this file for quick reference!** 🔖
