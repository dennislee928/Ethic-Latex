# Multi-stage Dockerfile for the ERH Engine (REST + gRPC).
# IMPORTANT: Build context MUST be the repository root (.) so erh_core is copied.
#
#   docker build -f erh_engine/Dockerfile -t erh-engine .
#   docker run -p 8000:8000 -p 50051:50051 erh-engine
#
# REST default :8000, gRPC :50051. Set ERH_MODE=rest|grpc|both (default both).

FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY erh_engine/requirements.txt ./erh_engine/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r erh_engine/requirements.txt

# Canonical algorithm + the service layer (paths relative to repo root context).
COPY erh_core/ ./erh_core/
COPY erh_engine/ ./erh_engine/

ENV PYTHONPATH=/app
ENV ERH_MODE=both

EXPOSE 8000 50051

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/v1/health || exit 1

CMD ["python", "-m", "erh_engine.serve"]
