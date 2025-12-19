# Multi-stage Dockerfile for FastAPI Backend
# Build context should be from repository root

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies for Postgres and Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY erh-security-app/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY erh-security-app/backend/ ./erh-security-app/backend/
COPY erh_core/ ./erh_core/
COPY simulation/ ./simulation/

# Set Python path to include project root
ENV PYTHONPATH=/app

# Expose port (use PORT env var for cloud platforms, default to 8000)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run migrations and start server
# Note: Migrations are run with || true to allow graceful startup if DB is not ready
CMD ["sh", "-c", "cd erh-security-app/backend && (alembic upgrade head || true) && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

