# Stage 1: Build Vue.js frontend
FROM node:22-alpine AS frontend-build

WORKDIR /app

# Set npm timeouts and disable optional dependencies to speed up install
RUN npm config set fetch-timeout 120000 && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000

# Copy package files
COPY package.json package-lock.json ./

# Use npm ci instead of npm install (deterministic, better for CI/CD)
# Remove --ignore-engines; if there's a conflict, it should be fixed in package.json
RUN npm ci --prefer-offline --no-audit

# Copy source code
COPY src/ ./src/

# Copy individual config files
COPY index.html .
COPY vite.config.ts .
COPY vitest.config.ts .
COPY tsconfig.json .
COPY tsconfig.app.json .
COPY tsconfig.node.json .
COPY tsconfig.vitest.json .
COPY env.d.ts .

# Build frontend
RUN npm run build && npm cache clean --force

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

# Health check (Cloud Run will handle this, but good for local testing)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Run Flask with Gunicorn
# Cloud Run requires the app to listen on 0.0.0.0:$PORT
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers ${GUNICORN_WORKERS} --threads 2 --timeout 120 --access-logfile - --error-logfile - --log-level info backend.app:app"]