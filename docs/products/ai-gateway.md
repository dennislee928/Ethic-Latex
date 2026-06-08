# AI Gateway / LLM-DR

Detect and block the **point-collapse** where an LLM's ethical/logical judgment
degrades as prompt complexity grows. Three deployment shapes share the same
`erh_engine` core via the `llm` adapter (`erh_engine/adapters/llm.py`).

For each exchange: `x` = prompt complexity, `V` = the safe/expected pole,
`J` = safety value of the actual response, `delta = J − V` spikes on jailbreak
compliance or over-refusal.

## 1. Runtime AI firewall (Go/Gin)

`services/ai-gateway/` — reverse proxy in front of an LLM upstream. Scores every
exchange over gRPC and blocks responses above `MAX_RISK`. Fail-closed.

```bash
PYTHONPATH=. ERH_GRPC_PORT=50051 python -m erh_engine.grpc.server &
cd services/ai-gateway && ERH_ENGINE_ADDR=localhost:50051 MAX_RISK=50 go run .
curl -X POST localhost:8080/v1/chat -d '{"prompt":"What is the capital of France?"}'
```

## 2. CI/CD pipeline gate

`erh_engine/cli.py` runs a jailbreak/system-prompt test suite through the model
and fails the pipeline on high divergence.

```bash
python -m erh_engine.cli --cases erh_engine/examples/llm_gate_cases.json --max-risk 50
# live: --provider openai --model gpt-4o   (uses OPENAI_API_KEY)
```

GitHub Action: `.github/actions/erh-gate/` (workflow `.github/workflows/erh-llm-gate.yml`).

## 3. Kubernetes sidecar

`deploy/k8s/erh-sidecar/` — engine runs beside the app over `localhost:50051`.
