# ERH AI Gateway (runtime AI firewall)

A Go/Gin reverse proxy that fronts an LLM upstream, scores every exchange with
the Python **erh_engine** over gRPC, and blocks responses whose ERH misjudgment
risk exceeds a threshold. This is the high-concurrency *edge* of the hybrid
architecture — all ERH math stays in `erh_engine`, reached via gRPC.

## Run locally

```bash
# 1. start the engine (gRPC)
PYTHONPATH=. ERH_GRPC_PORT=50051 python -m erh_engine.grpc.server

# 2. start the gateway
cd services/ai-gateway
ERH_ENGINE_ADDR=localhost:50051 MAX_RISK=50 \
  LLM_API_KEY=sk-... LLM_MODEL=gpt-4o-mini go run .

# 3. call it
curl -s -X POST localhost:8080/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"What is the capital of France?"}'
```

Without `LLM_API_KEY` the upstream is stubbed (echoes the prompt) so the
firewall path is fully testable offline.

## Config (env)

| Var | Default | Meaning |
|-----|---------|---------|
| `GATEWAY_ADDR` | `:8080` | Listen address |
| `ERH_ENGINE_ADDR` | `localhost:50051` | erh_engine gRPC address |
| `LLM_UPSTREAM_URL` | OpenAI chat completions | Upstream endpoint |
| `LLM_API_KEY` | — | Upstream bearer token (stub if empty) |
| `LLM_MODEL` | `gpt-4o-mini` | Upstream model |
| `MAX_RISK` | `50` | Block when `risk_score` exceeds this |

## Regenerate gRPC stubs

```bash
protoc -I ../../erh_engine/proto \
  --go_out=pb --go_opt=paths=source_relative,Merh_engine.proto=github.com/dennislee928/ethic-latex/ai-gateway/pb \
  --go-grpc_out=pb --go-grpc_opt=paths=source_relative,Merh_engine.proto=github.com/dennislee928/ethic-latex/ai-gateway/pb \
  ../../erh_engine/proto/erh_engine.proto
```

Behavior is fail-closed: if the engine is unreachable the gateway returns 503
rather than leaking an unvetted response.
