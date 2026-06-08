# ERH Engine — Kubernetes Sidecar Pattern

Deploy the ERH engine as a sidecar so application microservices can ERH-validate
high-risk logic decisions over `localhost:50051` (gRPC) with minimal latency.

## Manifests

- `deployment.yaml` — generic app + `erh-engine` sidecar (replace `your-app:latest`).
- `gateway-deployment.yaml` — the AI-gateway firewall + engine sidecar, exposed via a Service.

## Build & push images

```bash
# engine (build context = repo root)
docker build -f erh_engine/Dockerfile -t ghcr.io/dennislee928/erh-engine:latest .
# gateway
docker build -t ghcr.io/dennislee928/erh-ai-gateway:latest services/ai-gateway
docker push ghcr.io/dennislee928/erh-engine:latest
docker push ghcr.io/dennislee928/erh-ai-gateway:latest
```

## Try on a local cluster (kind/minikube)

```bash
kubectl apply -f deploy/k8s/erh-sidecar/gateway-deployment.yaml
kubectl create secret generic llm-credentials --from-literal=api-key=sk-...
kubectl port-forward svc/erh-ai-gateway 8080:80
curl -X POST localhost:8080/v1/chat -d '{"prompt":"hello"}'
```
