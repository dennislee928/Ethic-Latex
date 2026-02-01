# Dockerfile for Ethical Riemann Hypothesis
# Multi-stage build for production deployment

# Stage 1: Base with system dependencies
FROM python:3.10-slim AS base
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies
FROM base AS dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Quantum (optional extras)
FROM dependencies AS quantum
RUN pip install --no-cache-dir qiskit>=1.0.0 qiskit-aer>=0.14.0 qiskit-ibm-runtime>=0.21.0 || true

# Stage 4: Application
FROM quantum AS app
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e . || pip install --no-cache-dir -r requirements.txt

EXPOSE 8888 8501 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8888')" 2>/dev/null || exit 1

CMD ["python", "-m", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
