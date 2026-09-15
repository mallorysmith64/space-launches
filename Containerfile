# Stage 1: Build Vue.js frontend
FROM node:22-alpine AS frontend-build

WORKDIR /app

# Skip Playwright browser downloads (not needed for build)
# This prevents hanging on @playwright/test during npm ci
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# npm configuration for reliability in constrained environments
ENV npm_config_fetch_timeout=600000 \
    npm_config_fetch_retries=10 \
    npm_config_fetch_retry_mintimeout=30000 \
    npm_config_fetch_retry_maxtimeout=120000 \
    npm_config_registry=https://registry.npmjs.org/

# Clear npm cache
RUN npm cache clean --force

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
# --no-optional: Skip optional deps that slow things down
# --prefer-offline: Use cache if available
# --maxsockets 8: Parallel downloads
RUN npm ci \
    --prefer-offline \
    --no-optional \
    --no-audit \
    --loglevel warn \
    --maxsockets 8

# Copy source code
COPY src/ ./src/

# Copy config files
COPY index.html .
COPY vite.config.ts .
COPY vitest.config.ts .
COPY tsconfig.json .
COPY tsconfig.app.json .
COPY tsconfig.node.json .
COPY tsconfig.vitest.json .
COPY env.d.ts .

# Build frontend
RUN npm run build

# Clean up cache
RUN npm cache clean --force && rm -rf node_modules/.cache

# Stage 2: Runtime with Flask backend and frontend
FROM python:3.12-slim

WORKDIR /app

# Cloud Run requires PORT environment variable
ENV PORT=5000 \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GUNICORN_WORKERS=2

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./backend/

# Copy built frontend from previous stage
COPY --from=frontend-build /app/dist ./frontend/dist

# Copy static images and data
COPY src/images ./src/images
COPY src/data ./src/data

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check for local testing
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Run Flask with Gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers ${GUNICORN_WORKERS} --threads 2 --timeout 120 --access-logfile - --error-logfile - --log-level info backend.app:app"]