#!/bin/bash
# Build multi-architecture container images for NotebookLM MCP Server
# Supports: linux/amd64, linux/arm64

set -e

# Configuration
IMAGE_NAME="${IMAGE_NAME:-notebooklm-mcp}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-ghcr.io/yourusername}"
BUILD_TOOL="${BUILD_TOOL:-podman}"  # podman only (docker support removed)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v ${BUILD_TOOL} &> /dev/null; then
        log_error "${BUILD_TOOL} is not installed"
        exit 1
    fi

    log_success "Build tool: ${BUILD_TOOL} $(${BUILD_TOOL} --version | head -1)"

    # Check for QEMU if cross-building
    if command -v qemu-aarch64-static &> /dev/null; then
        log_success "QEMU found - cross-platform builds supported"
    else
        log_warning "QEMU not found - cross-platform builds may fail"
    fi
}

# Build for single architecture
build_single_arch() {
    local platform=$1
    local arch_tag=$2

    log_info "Building for ${platform}..."

    ${BUILD_TOOL} build \
        --platform ${platform} \
        -t ${IMAGE_NAME}:${arch_tag} \
        -f Containerfile \
        .

    log_success "Built ${IMAGE_NAME}:${arch_tag}"
}

# Create and push multi-arch manifest
create_manifest() {
    log_info "Creating multi-arch manifest..."

    # Create manifest
    ${BUILD_TOOL} manifest create ${IMAGE_NAME}:${IMAGE_TAG} \
        ${IMAGE_NAME}:${IMAGE_TAG}-arm64 \
        ${IMAGE_NAME}:${IMAGE_TAG}-amd64

    log_success "Manifest created: ${IMAGE_NAME}:${IMAGE_TAG}"

    # Inspect manifest
    log_info "Manifest details:"
    ${BUILD_TOOL} manifest inspect ${IMAGE_NAME}:${IMAGE_TAG}
}

# Push manifest to registry
push_manifest() {
    local target="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

    log_info "Pushing to ${target}..."

    ${BUILD_TOOL} manifest push ${IMAGE_NAME}:${IMAGE_TAG} docker://${target}

    log_success "Pushed to ${target}"
}

# Main build process
main() {
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "  NotebookLM MCP Multi-Architecture Build"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    echo "Image Name: ${IMAGE_NAME}"
    echo "Image Tag:  ${IMAGE_TAG}"
    echo "Registry:   ${REGISTRY}"
    echo "Tool:       ${BUILD_TOOL}"
    echo ""

    check_prerequisites

    echo ""
    log_info "Starting multi-architecture build..."
    echo ""

    # Build ARM64
    build_single_arch "linux/arm64" "${IMAGE_TAG}-arm64"
    echo ""

    # Build AMD64
    build_single_arch "linux/amd64" "${IMAGE_TAG}-amd64"
    echo ""

    # Create manifest
    create_manifest
    echo ""

    # Ask to push
    read -p "$(echo -e ${YELLOW}Push to registry ${REGISTRY}? [y/N]:${NC} )" -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        push_manifest
    else
        log_info "Skipped push to registry"
        log_info "To push manually run:"
        echo "  ${BUILD_TOOL} manifest push ${IMAGE_NAME}:${IMAGE_TAG} docker://${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    fi

    echo ""
    log_success "Multi-architecture build complete!"
    echo ""
    echo "Available tags:"
    echo "  - ${IMAGE_NAME}:${IMAGE_TAG} (multi-arch)"
    echo "  - ${IMAGE_NAME}:${IMAGE_TAG}-arm64"
    echo "  - ${IMAGE_NAME}:${IMAGE_TAG}-amd64"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --tool)
            BUILD_TOOL="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --image NAME      Image name (default: notebooklm-mcp)"
            echo "  --tag TAG         Image tag (default: latest)"
            echo "  --registry REG    Container registry (default: ghcr.io/yourusername)"
            echo "  --tool TOOL       Build tool: podman only (default: podman)"
            echo "  --help            Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  IMAGE_NAME        Same as --image"
            echo "  IMAGE_TAG         Same as --tag"
            echo "  REGISTRY          Same as --registry"
            echo "  BUILD_TOOL        Same as --tool"
            echo ""
            echo "Examples:"
            echo "  $0"
            echo "  $0 --tag v1.0.0"
            echo "  $0 --registry ghcr.io/myorg --tag v1.0.0"
            echo "  IMAGE_NAME=my-app IMAGE_TAG=dev $0"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Run '$0 --help' for usage information"
            exit 1
            ;;
    esac
done

# Run main
main
