# ERH Security App - Multi-stage build
# Build from repo root: docker build -f erh-security-app/Dockerfile --target backend erh-security-app
# Or from this dir: docker build -f Dockerfile --target backend .

# Stage 1: Backend (FastAPI)
FROM python:3.10-slim AS backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 2: Frontend (Next.js) - requires package.json in frontend/
FROM node:20-alpine AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
