# Stage 1: Build Vue.js frontend
FROM node:22.22.2 AS frontend-build

WORKDIR /app

# Copy package files (multiple files = must end with /)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY src/ ./src/

# Copy individual config files (single file = can use .)
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

# Stage 2: Runtime with Flask backend and frontend
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
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

# Copy static images and data (baked into the image so they're present
# even without the local volume mount used in podman-compose/dev)
COPY src/images ./src/images
COPY src/data ./src/data

# Expose port
EXPOSE 5000

# Environment variables
ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    GUNICORN_WORKERS=4

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run Flask with Gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:5000 --workers ${GUNICORN_WORKERS} --timeout 120 --access-logfile - --error-logfile - --log-level info backend.app:app"]