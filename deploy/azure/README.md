# Azure Deployment

## Option 1: Container Instances

```bash
az container create \
  --resource-group your-rg \
  --name erh-app \
  --image your-registry/erh-app \
  --dns-name-label your-app-name \
  --ports 8501
```

## Option 2: App Service

Use Azure App Service with Docker support.

## Option 3: Kubernetes

Deploy to AKS (Azure Kubernetes Service).

