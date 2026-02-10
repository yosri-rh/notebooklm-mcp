# Multi-Architecture Build Support

## Overview

✅ **YES** - The NotebookLM MCP container **fully supports** both ARM64 and AMD64 architectures.

## Architecture Compatibility

### Supported Platforms

| Platform | Support | Status | Notes |
|----------|---------|--------|-------|
| **linux/amd64** | ✅ Full | Production Ready | x86_64, Intel/AMD 64-bit |
| **linux/arm64** | ✅ Full | Production Ready | ARMv8, Apple Silicon, AWS Graviton |

### Component Compatibility

| Component | ARM64 | AMD64 | Notes |
|-----------|-------|-------|-------|
| **Python 3.12** | ✅ | ✅ | Official multi-arch images |
| **uv package manager** | ✅ | ✅ | Auto-detects architecture |
| **Playwright** | ✅ | ✅ | Downloads arch-specific Chromium |
| **Chromium browser** | ✅ | ✅ | Playwright bundles for both archs |
| **System libraries** | ✅ | ✅ | Debian packages available for both |
| **Python dependencies** | ✅ | ✅ | Pure Python or multi-arch wheels |

## Why It Works

### 1. Base Images
```dockerfile
FROM python:3.12-slim
```
- Official Python images are multi-arch
- Available for: linux/amd64, linux/arm64/v8, linux/386, linux/arm/v7, and more
- Automatically pulls correct architecture

### 2. Package Manager (uv)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
- Install script detects system architecture automatically
- Downloads correct binary for ARM64 or AMD64

### 3. Playwright/Chromium
```bash
uv run playwright install chromium
```
- Playwright detects architecture at install time
- Downloads appropriate Chromium binary:
  - **ARM64**: Chrome for Testing (arm64)
  - **AMD64**: Chrome for Testing (x86_64)

### 4. System Dependencies
All Chromium dependencies are standard Debian packages:
```dockerfile
RUN apt-get install -y libnss3 libnspr4 libatk1.0-0 ...
```
- Available in Debian repos for all architectures
- No custom compilation needed

## Building for Multiple Architectures

### Method 1: Native Build (Recommended)

Build on the target platform for best performance:

```bash
# On ARM64 machine (e.g., Apple Silicon Mac, AWS Graviton)
podman build -t notebooklm-mcp:arm64 .

# On AMD64 machine (e.g., Intel/AMD server)
podman build -t notebooklm-mcp:amd64 .
```

### Method 2: Cross-Platform Build (Using QEMU)

Build for different architecture using emulation:

```bash
# On ARM64, build for AMD64
podman build --platform linux/amd64 -t notebooklm-mcp:amd64 .

# On AMD64, build for ARM64
podman build --platform linux/arm64 -t notebooklm-mcp:arm64 .
```

⚠️ **Note**: Cross-platform builds use QEMU emulation and are significantly slower.

### Method 3: Multi-Arch Manifest (Best for Distribution)

Create a single image tag that supports both architectures:

#### Using Podman Manifest

```bash
# Create manifest list
podman manifest create notebooklm-mcp:latest

# Build and add ARM64 image
podman build --platform linux/arm64 -t notebooklm-mcp:arm64 .
podman manifest add notebooklm-mcp:latest notebooklm-mcp:arm64

# Build and add AMD64 image
podman build --platform linux/amd64 -t notebooklm-mcp:amd64 .
podman manifest add notebooklm-mcp:latest notebooklm-mcp:amd64

# Push multi-arch image
podman manifest push notebooklm-mcp:latest docker://ghcr.io/yourusername/notebooklm-mcp:latest
```

#### Using Docker Buildx

```bash
# Create and use buildx builder
docker buildx create --name multiarch --use

# Build and push multi-arch image in one command
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/yourusername/notebooklm-mcp:latest \
  --push \
  .
```

### Method 4: GitHub Actions (CI/CD)

See `.github/workflows/docker-publish.yml` - already configured for multi-arch!

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ${{ steps.meta.outputs.tags }}
```

## Build Scripts

### build-multiarch.sh

```bash
#!/bin/bash
# Build multi-architecture images

set -e

IMAGE_NAME="${1:-notebooklm-mcp}"
IMAGE_TAG="${2:-latest}"
REGISTRY="${3:-ghcr.io/yourusername}"

echo "Building multi-architecture image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Create manifest
podman manifest create ${IMAGE_NAME}:${IMAGE_TAG}

# Build ARM64
echo "Building for linux/arm64..."
podman build \
  --platform linux/arm64 \
  -t ${IMAGE_NAME}:${IMAGE_TAG}-arm64 \
  .
podman manifest add ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:${IMAGE_TAG}-arm64

# Build AMD64
echo "Building for linux/amd64..."
podman build \
  --platform linux/amd64 \
  -t ${IMAGE_NAME}:${IMAGE_TAG}-amd64 \
  .
podman manifest add ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:${IMAGE_TAG}-amd64

# Inspect manifest
echo "Manifest created:"
podman manifest inspect ${IMAGE_NAME}:${IMAGE_TAG}

echo ""
echo "To push: podman manifest push ${IMAGE_NAME}:${IMAGE_TAG} docker://${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
```

## Testing Multi-Arch Images

### Verify Architecture

```bash
# Check what architecture an image was built for
podman inspect notebooklm-mcp:latest | jq '.[0].Architecture'

# Check manifest for multi-arch support
podman manifest inspect notebooklm-mcp:latest | jq '.manifests[].platform'
```

### Test on Different Platforms

```bash
# Pull and run - automatically selects correct architecture
podman run --platform linux/amd64 notebooklm-mcp:latest uname -m
# Output: x86_64

podman run --platform linux/arm64 notebooklm-mcp:latest uname -m
# Output: aarch64
```

## OpenShift Deployment Considerations

### Multi-Architecture Clusters

OpenShift 4.19 supports heterogeneous clusters with mixed architectures:

```yaml
# Deployment will automatically use correct architecture
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: notebooklm-mcp
        image: ghcr.io/yourusername/notebooklm-mcp:latest
        # No platform specification needed - uses node architecture
```

### Architecture-Specific Node Selection

If you want to pin to specific architecture:

```yaml
spec:
  template:
    spec:
      nodeSelector:
        kubernetes.io/arch: arm64  # or amd64
```

### ImageStream with Multi-Arch

```yaml
apiVersion: image.openshift.io/v1
kind: ImageStream
metadata:
  name: notebooklm-mcp
spec:
  tags:
  - name: latest
    from:
      kind: DockerImage
      name: ghcr.io/yourusername/notebooklm-mcp:latest
    importPolicy:
      scheduled: true
    # ImageStream will maintain both architecture variants
```

## Performance Considerations

### Build Times

| Method | ARM64 Build | AMD64 Build | Notes |
|--------|-------------|-------------|-------|
| Native | ~5-10 min | ~5-10 min | Fastest |
| Cross (QEMU) | ~20-40 min | ~20-40 min | 3-5x slower |
| CI/CD Parallel | ~10-15 min total | ~10-15 min total | Builds in parallel |

### Runtime Performance

- **Native**: Full native performance
- **Cross**: No performance penalty (only build is slow, runtime uses native arch)
- **Image Size**: Same size for both architectures (~800MB)

## Container Registry Support

All major registries support multi-arch manifests:

| Registry | Multi-Arch Support | Notes |
|----------|-------------------|-------|
| **GitHub Container Registry** | ✅ | ghcr.io |
| **Docker Hub** | ✅ | docker.io |
| **Quay.io** | ✅ | quay.io |
| **OpenShift Registry** | ✅ | Built-in support |
| **AWS ECR** | ✅ | Amazon container registry |
| **GCP Artifact Registry** | ✅ | Google container registry |

## Recommendations

### For Development
- Build natively on your development machine
- Use `--platform` flag only when testing cross-arch compatibility

### For CI/CD
- Use GitHub Actions with `docker/build-push-action`
- Build both architectures in parallel
- Push as multi-arch manifest

### For Production
- Always use multi-arch manifests
- Tag with semantic versioning: `v1.0.0`, `v1.0.0-arm64`, `v1.0.0-amd64`
- Pin to specific digest for reproducibility

## Example: Complete Multi-Arch Workflow

```bash
# 1. Build locally for current architecture
podman build -t notebooklm-mcp:dev .

# 2. Test locally
podman run --rm notebooklm-mcp:dev

# 3. Create multi-arch build for release
podman manifest create notebooklm-mcp:1.0.0

# 4. Build for both architectures (can run on separate machines)
podman build --platform linux/arm64 -t notebooklm-mcp:1.0.0-arm64 .
podman build --platform linux/amd64 -t notebooklm-mcp:1.0.0-amd64 .

# 5. Add to manifest
podman manifest add notebooklm-mcp:1.0.0 notebooklm-mcp:1.0.0-arm64
podman manifest add notebooklm-mcp:1.0.0 notebooklm-mcp:1.0.0-amd64

# 6. Push to registry
podman manifest push notebooklm-mcp:1.0.0 \
  docker://ghcr.io/yourusername/notebooklm-mcp:1.0.0

# 7. Deploy to OpenShift (works on both AMD64 and ARM64 nodes)
oc new-app ghcr.io/yourusername/notebooklm-mcp:1.0.0
```

## Troubleshooting

### Issue: "exec format error"
**Cause**: Trying to run image built for different architecture
**Solution**:
```bash
# Rebuild for correct platform
podman build --platform linux/$(uname -m) -t notebooklm-mcp .
```

### Issue: Playwright installation fails
**Cause**: Network issues or unsupported architecture
**Solution**:
```bash
# Playwright supports: linux/amd64, linux/arm64
# Check architecture inside container
podman run --rm notebooklm-mcp uname -m
```

### Issue: Slow build on cross-platform
**Cause**: QEMU emulation overhead
**Solution**: Build natively or use CI/CD with native runners

## Summary

✅ **The NotebookLM MCP container is fully multi-architecture compatible**

- **Works on**: Apple Silicon Macs, Intel/AMD servers, AWS Graviton, and more
- **No code changes needed**: Dockerfile already supports both architectures
- **Playwright/Chromium**: Automatically downloads correct binaries
- **OpenShift**: Deploys seamlessly on heterogeneous clusters
- **CI/CD**: GitHub Actions already configured for multi-arch builds

**You can build and deploy this container on any ARM64 or AMD64 platform without modification.**
