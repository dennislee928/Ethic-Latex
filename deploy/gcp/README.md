# Google Cloud Platform Deployment

## Option 1: Cloud Run (Recommended)

### Deploy Container

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/erh-app

# Deploy to Cloud Run
gcloud run deploy erh-app \
  --image gcr.io/YOUR_PROJECT/erh-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Option 2: Compute Engine

Similar to AWS EC2 setup.

## Option 3: App Engine

See `deploy/gcp/app.yaml`

