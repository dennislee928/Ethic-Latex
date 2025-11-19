# Docker Deployment Guide

## Build Image

```bash
docker build -t ethical-riemann-hypothesis .
```

## Run Locally

### Jupyter Notebook
```bash
docker run -p 8888:8888 \
  -v $(pwd)/simulation:/app/simulation \
  ethical-riemann-hypothesis \
  python -m notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

### Streamlit App
```bash
docker run -p 8501:8501 \
  -v $(pwd)/simulation:/app/simulation \
  ethical-riemann-hypothesis \
  streamlit run simulation/app.py --server.port=8501 --server.address=0.0.0.0
```

## Docker Compose

```bash
docker-compose up -d
```

Access:
- Jupyter: http://localhost:8888
- Streamlit: http://localhost:8501

## Push to Registry

```bash
# Tag
docker tag ethical-riemann-hypothesis your-registry/erh-app:latest

# Push
docker push your-registry/erh-app:latest
```

## Deploy to Cloud

Any cloud platform that supports Docker:
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform
- Railway
- Render

