# Stage 1: Build Vue.js frontend
FROM node:22-alpine AS frontend-build

WORKDIR /app

# Skip Playwright browser downloads - not needed for build
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --omit=optional --prefer-offline --no-audit

# Copy source code and config
COPY src/ ./src/
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

# Stage 2: Runtime with Flask backend
FROM python:3.12-slim

WORKDIR /app

# Cloud Run required variables
ENV PORT=5000 \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY --from=frontend-build /app/dist ./frontend/dist
COPY src/images ./src/images
COPY src/data ./src/data

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Run Flask with Gunicorn
CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 0 --access-logfile - --error-logfile - backend.app:app