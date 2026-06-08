# ERH Cloud-Native Products

These products generalize the Ethical Riemann Hypothesis from a research artifact
and LLM "ethical-degree" inspector into a **universal behavior/logic decision
evaluation engine**. Every product is a thin domain adapter over the same core:
it converts raw data into the generic `Sample` contract and asks one question —

> Does the cumulative error in critical misjudgments stay bounded
> (`|E(x)| ≤ C·x^(1/2+ε)`, healthy) as decision complexity `x` grows,
> or does it grow structurally (unhealthy / phase-transition / point-collapse)?

## Shared substrate: `erh_engine`

| Surface | Path | Endpoint |
|---------|------|----------|
| REST | `erh_engine/rest/main.py` | `POST /v1/evaluate`, `GET /v1/health` |
| gRPC | `erh_engine/grpc/server.py` | `ERHEngine.Evaluate` (`:50051`) |
| CLI | `erh_engine/cli.py` | `python -m erh_engine.cli` |

All math lives in `erh_core/` (`select_ethical_primes` → `compute_Pi_and_error`
→ `check_erh_bound_structured` → `analyze_error_growth`); `erh_engine` never
reimplements it.

Run it:

```bash
# REST + gRPC together
PYTHONPATH=. ERH_MODE=both python -m erh_engine.serve
# or containerized (build context = repo root)
docker build -f erh_engine/Dockerfile -t erh-engine . && docker run -p 8000:8000 -p 50051:50051 erh-engine
```

## Products

- [AI Gateway / LLM-DR](ai-gateway.md) — runtime AI firewall, CI/CD gate, K8s sidecar.
- [Cloud IAM / CSPM](iam-cspm.md) — least-privilege divergence audit (Zero Trust).
- [UEBA insider-threat](ueba.md) — behavioral convergence-domain drift detection.
- [Compliance mapping](compliance.md) — NIST AI RMF, CSA, MITRE ATT&CK IOB.
