# Multi-stage Dockerfile for NotebookLM MCP Server
# Optimized for production use with Playwright/Chromium support

# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Stage 2: Runtime stage
FROM python:3.12-slim

# Install runtime dependencies for Playwright/Chromium
RUN apt-get update && apt-get install -y \
    # Chromium dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    # Additional utilities
    curl \
    wget \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r notebooklm && useradd -r -g notebooklm notebooklm

# Install uv in runtime stage (as root, accessible to all)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=notebooklm:notebooklm . .

# Copy dependencies from builder
COPY --from=builder --chown=notebooklm:notebooklm /app/.venv /app/.venv

# Install Playwright browsers (as root, then change ownership)
RUN uv run playwright install chromium && \
    uv run playwright install-deps chromium && \
    chown -R notebooklm:notebooklm /root/.cache/ms-playwright 2>/dev/null || true

# Create directory for persistent Chrome user data
RUN mkdir -p /app/chrome-user-data && \
    chown -R notebooklm:notebooklm /app/chrome-user-data

# Switch to non-root user
USER notebooklm

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    NOTEBOOKLM_HEADLESS=true \
    LOG_LEVEL=INFO \
    PATH="/app/.venv/bin:$PATH"

# Expose port (if needed for health checks)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Set entrypoint - use .venv python directly
ENTRYPOINT ["/app/.venv/bin/python", "-m", "notebooklm_mcp.server"]
