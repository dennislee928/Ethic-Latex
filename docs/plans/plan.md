# Plan: ERH as a Universal Logic & Behavior Decision Engine — Enterprise Cloud-Native Products

> **Deliverable location:** On execution, this plan is to be saved as
> `/Users/dennis_leedennis_lee/Documents/GitHub/Ethic-Latex/docs/plans/plan.md`.
> (During plan mode only the harness plan file is editable; the content is identical.)

## Progress / Status (resume here)

> Updated incrementally during implementation on branch `feature/erh-engine`.

- [x] **Phase 0 — `erh_engine` interface (REST + gRPC)** — DONE & tested.
  - `erh_engine/contracts/schemas.py` (Sample/EvaluateRequest/EvaluateResponse).
  - `erh_engine/engine.py` (`evaluate()` wraps erh_core; NaN-safe; carries context).
  - `erh_engine/rest/main.py` (`/v1/health`, `/v1/evaluate` + adapter routers).
  - `erh_engine/proto/erh_engine.proto` + generated stubs + `grpc/server.py` + `translate.py`.
  - `erh_engine/serve.py` (ERH_MODE rest|grpc|both), `Dockerfile`, `requirements.txt`.
  - Adapters: `adapters/{scoring,llm,iam_cspm,ueba}.py` (live path + fallback).
  - Tests: `tests/erh_engine_tests/test_engine.py` — **7 passing** (REST↔gRPC↔direct parity).
  - NOTE: installed `grpcio`/`grpcio-tools` into `.venv`. Run tests with
    `PYTHONPATH=. .venv/bin/python -m pytest tests/erh_engine_tests/ -q`.
- [x] **Phase 1 — AI Gateway** — DONE & tested.
  - CLI gate `erh_engine/cli.py` (+ example cases) — verified PASS/FAIL exit codes.
  - GH composite action `.github/actions/erh-gate/` + workflow `.github/workflows/erh-llm-gate.yml`.
  - Go/Gin firewall `services/ai-gateway/` — **builds + vets clean**, e2e tested:
    benign passes, harmful blocked via Go→Python gRPC. Dockerfile + README.
  - K8s sidecar manifests `deploy/k8s/erh-sidecar/` (app+engine, gateway+engine).
- [ ] **Phase 2 — IAM/CSPM**: adapter + `/v1/iam/audit` DONE in Phase 0; remaining =
  docs + example. (Optional Go dispatch center reuses gateway skeleton — deferred.)
- [ ] **Phase 3 — UEBA**: adapter + `/v1/ueba/evaluate` DONE in Phase 0; remaining =
  Next.js dashboard route in `erh-security-app/frontend/`.
- [ ] **Phase 4 — SDKs/docs/CI**: extend `erh`+`erh-js-sdk` with `evaluate()`; docs/products/*;
  update README + SUPPORTED_SURFACES; CI workflows for engine + gateway.

## Context

Today the ERH framework's value is mostly framed as research + an LLM "ethical-degree"
desktop inspector. The codebase, however, already contains a clean, reusable scoring engine
and a partial service layer:

- **Canonical engine** (`erh_core/`): `judge_and_check_erh()`, `check_erh_bound_structured()`
  (`erh_core/analysis/erh_checks.py`), `compute_Pi_and_error`, `analyze_error_growth`,
  `select_ethical_primes` (`erh_core/core/ethical_primes.py`), pluggable judges/oracles
  (`erh_core/core/judgement_system.py`), `MetaMonitor` (`erh_core/core/meta_monitor.py`).
- **Existing REST**: `simulation/api/main.py` (`/health`, `/simulate`) and a richer FastAPI
  backend `erh-security-app/backend/` (routers: ingestion, analysis, verify, rules, simulate)
  that already maps external data (GitLab MR/SAST) → ERH metrics
  (`app/erh_security/mapping.py`, `metrics.py`).
- **No gRPC, no shared "ERH scoring contract"** exists yet. Each surface re-implements its
  own mapping. Deployment exists (`infra/fastapi/Dockerfile`, `render.yaml`, GH Actions).

**Goal:** generalize ERH from "LLM prompt guard" into a *universal behavior/logic decision
evaluation engine* exposed through one standardized, containerized, low-latency interface
(REST + gRPC), then build four enterprise products on top:

1. **AI Gateway / LLM-DR** — runtime AI firewall + CI/CD pipeline gate + K8s sidecar.
2. **Cloud IAM Logic Audit / Zero Trust (CSPM)** — divergence from least-privilege baseline.
3. **UEBA insider-threat** — behavioral convergence-domain drift detection.
4. **Standardized ERH service interface** — the shared substrate for products 1–3.

**Decisions (confirmed with user):** all four products, full breadth, phased; **hybrid**
language (Python ERH core service + thin Go/Gin edge proxy on hot paths); **live**
integrations (real LLM provider, real cloud IAM, real SIEM/log sources) with adapter seams.

---

## Architecture Overview

```
                       ┌──────────────────────────────────────────┐
   clients / CI / k8s  │              edge (Go/Gin)                │
   ───────────────────▶│  ai-gateway proxy · sidecar (hot path)   │
                       └───────────────┬──────────────────────────┘
                                       │ gRPC (low-latency) / REST
                       ┌───────────────▼──────────────────────────┐
                       │      erh-engine service (Python)          │
                       │  EvaluateRequest → EvaluateResponse       │
                       │  wraps judge_and_check_erh / MetaMonitor  │
                       └───────────────┬──────────────────────────┘
                                       │ in-process
                       ┌───────────────▼──────────────────────────┐
                       │  erh_core  (canonical algorithm, reused)  │
                       └──────────────────────────────────────────┘

   domain adapters (Python): llm · iam_cspm · ueba  →  emit Action/Judgment/GroundTruth/Importance
```

**Key reuse principle:** every product is a *domain adapter* that converts its raw data
(LLM responses, IAM policies, user-behavior events) into the existing `Action` /
`Judgment` / `GroundTruth` / `Importance` shape, then calls the *same* engine. The mapping
already done for security in `erh-security-app/backend/app/erh_security/mapping.py` is the
template to follow.

---

## Phase 0 — Standardized ERH Engine Interface (foundation; build first)

New top-level package: `erh_engine/` (a thin service layer over `erh_core`, no algorithm
duplication).

- **Contract** (`erh_engine/contracts/`): define one canonical `EvaluateRequest` /
  `EvaluateResponse` Pydantic schema + a matching `proto/erh_engine.proto`.
  - `EvaluateRequest`: list of generic `Sample{ id, complexity, value(V), judgment(J),
    weight(w), context: dict }` + params `{ tau, C, epsilon, baseline, slack_factor }`.
  - `EvaluateResponse`: reuse `ERHCheckResult` fields (`erh_satisfied`, `violation_rate`,
    `max_ratio`, `estimated_exponent`/α, `bound_value`) + `risk_score` (0–100) + per-sample
    `primes`/`delta` + optional `curves` (Pi(x), E(x)).
- **Engine adapter** (`erh_engine/engine.py`): map `Sample[]` → `erh_core` `Action` list,
  call `select_ethical_primes` → `compute_Pi_and_error` → `judge_and_check_erh` /
  `check_erh_bound_structured` → `analyze_error_growth`. Single function `evaluate(req)`.
  Reuse `erh-security-app/backend/app/erh_security/metrics.py::analyze_erh_structure` logic
  as reference; promote the generic parts here.
- **REST server** (`erh_engine/rest/main.py`, FastAPI): `POST /v1/evaluate`,
  `GET /v1/health`, `POST /v1/monitor/stream` (streaming `E(x,t)` via `MetaMonitor`).
- **gRPC server** (`erh_engine/grpc/server.py`): generate from `erh_engine.proto`; same
  `Evaluate` method. This is the low-latency path for the sidecar.
- **Containerization**: `erh_engine/Dockerfile` (multi-stage, sets `PYTHONPATH` to include
  `erh_core`), extend `infra/fastapi` pattern. Expose REST :8000 + gRPC :50051.
- **Tests**: `tests/erh_engine/` — golden test that REST and gRPC return identical results
  for the same input, plus parity against direct `judge_and_check_erh` call.

Representative files to create: `erh_engine/contracts/schemas.py`,
`erh_engine/proto/erh_engine.proto`, `erh_engine/engine.py`, `erh_engine/rest/main.py`,
`erh_engine/grpc/server.py`, `erh_engine/Dockerfile`.

---

## Phase 1 — AI Gateway / LLM-DR (Product 1)

### 1a. LLM domain adapter (Python)
`erh_engine/adapters/llm.py`: turn an LLM exchange into `Sample[]`.
- Complexity `x` = prompt/task complexity (token count, nesting, # of constraints).
- `V(a)` (ground truth proxy) via existing `HuggingFaceEthicalOracle` /
  `OracleDrivenJudge` (`erh_core/core/judgement_system.py`) — toxicity/safety → [-1,1].
- `J(a)` = the model's actual response score. `delta` = drift. Reuse jailbreak corpora in
  `llm_stress_test_results/` for seed cases.

### 1b. Runtime AI Firewall (Go/Gin edge proxy)
New `services/ai-gateway/` (Go module). Reverse proxy in front of LLM API calls:
- Intercept request/response, call `erh_engine` `Evaluate` over gRPC, block/redact when
  `risk_score` or `violation_rate` exceeds a configurable threshold; else pass through.
- Live integration: configurable upstream (OpenAI/Anthropic/etc.) via env; streaming-safe.
- `services/ai-gateway/Dockerfile`, config via env, structured audit logs (IOB-style).

### 1c. CI/CD pipeline gate (CLI + container)
`erh_engine/cli.py` (Python `erh-gate` entrypoint) + reuse `js-sdk` for a JS variant.
- Runs a suite of jailbreak/system-prompt test cases through the target LLM, scores via
  `Evaluate`, exits non-zero (fails pipeline) when "misjudgment divergence" too high.
- Ship `.github/actions/erh-gate/action.yml` (composite action) + example workflow
  `.github/workflows/erh-llm-gate.yml`. Containerized image reused from Phase 0.

### 1d. Kubernetes sidecar
`deploy/k8s/erh-sidecar/`: Pod spec running `erh_engine` gRPC server as a sidecar; sample
app talks to it over `localhost:50051`. Helm-lite manifests + README.

---

## Phase 2 — Cloud IAM Logic Audit / Zero Trust CSPM (Product 2)

`erh_engine/adapters/iam_cspm.py`:
- **Live integration**: pull IAM policies/ACLs (AWS IAM / GCP IAM — start with one, adapter
  seam for the other) via cloud SDK.
- Map each policy/grant → `Sample`: complexity `x` = breadth of the policy (actions ×
  resources × principals); `V(a)` = least-privilege baseline (minimal grant needed);
  `J(a)` = actual granted scope. `delta` = over-permission. `weight` = asset criticality /
  internet-exposure (reuse `Importance` semantics from security mapping).
- `select_ethical_primes` surfaces the critical over-grants; α / `violation_rate` flags
  "logical privilege escalation" risk. Block publish when growth-rate exceeds threshold.
- Surface via `erh_engine` REST `POST /v1/iam/audit`; optional Go/Gin "rule dispatch center"
  reusing the AI-gateway service skeleton.
- Data-source alignment: map findings to MITRE ATT&CK IOB indicators in response metadata.

---

## Phase 3 — UEBA Insider-Threat (Product 3)

`erh_engine/adapters/ueba.py`:
- **Live integration**: ingest user/entity event logs (login, access, location, download
  volume) from a SIEM source / log files. Adapter seam mirrors
  `erh-security-app/backend/app/ingestion/` (GitLab client + mock fallback).
- Per-user **behavioral convergence domain**: baseline normal behavior; map each event to a
  `Sample` where `delta` = deviation from the user's convergence domain; rising α / E(x)
  growth ⇒ behavior leaving the bound ⇒ raise risk score. Use temporal engine
  (`erh_core/core/temporal_erh.py`, `MetaMonitor`) for drift over time.
- Visualization: extend the existing Next.js security frontend
  (`erh-security-app/frontend/`) — add a UEBA dashboard route rendering "behavior deviation
  trajectory" from `erh_engine` curve/heatmap responses (reuse existing
  `/analysis/curves`, `/analysis/heatmap` patterns).

---

## Phase 4 — Cross-cutting: packaging, docs, governance

- **SDKs**: extend `erh` (PyPI) and `erh-js-sdk` (npm) with an `evaluate()` client method +
  gRPC stub (Python) so external systems call the standardized interface.
- **Docs**: `docs/products/` pages per product; update `README.md` "What This Repository Can
  Do" and `docs/SUPPORTED_SURFACES.md` to list `erh_engine` as a canonical surface.
- **Compliance mapping**: short doc tying products to NIST AI RMF (Measure/Manage), CSA LLM
  security guidance, MITRE ATT&CK IOB — as positioning, in `docs/products/compliance.md`.
- **CI/CD**: add build/test/push for `erh_engine` (REST+gRPC images) and `ai-gateway` (Go)
  to `.github/workflows/`, following `.github/workflows/erh_security_app.yml`.

---

## Critical files

| Area | Reuse (existing) | Create (new) |
|---|---|---|
| Engine core | `erh_core/analysis/erh_checks.py`, `erh_core/core/ethical_primes.py`, `judgement_system.py`, `meta_monitor.py`, `temporal_erh.py` | — |
| Mapping template | `erh-security-app/backend/app/erh_security/mapping.py`, `metrics.py` | `erh_engine/engine.py` |
| Contract/service | `simulation/api/main.py`, `erh-security-app/backend/app/main.py` | `erh_engine/contracts/schemas.py`, `proto/erh_engine.proto`, `rest/main.py`, `grpc/server.py` |
| Adapters | `HuggingFaceEthicalOracle`, ingestion clients | `erh_engine/adapters/{llm,iam_cspm,ueba}.py` |
| Edge proxy | — | `services/ai-gateway/` (Go/Gin) |
| CI/CD gate | `js-sdk/`, `erh/client.py` | `erh_engine/cli.py`, `.github/actions/erh-gate/` |
| K8s | `infra/fastapi/Dockerfile` | `deploy/k8s/erh-sidecar/` |
| Frontend | `erh-security-app/frontend/` | UEBA dashboard route |

---

## Verification

- **Phase 0:** `pytest tests/erh_engine/` — REST vs gRPC parity + parity against direct
  `judge_and_check_erh`. `docker build erh_engine/` then `curl POST /v1/evaluate` with a
  sample payload and confirm `erh_satisfied`/`risk_score`. `grpcurl` the `Evaluate` method.
- **Phase 1:** Run `ai-gateway` against a live LLM upstream; send a benign prompt (passes)
  and a known jailbreak from `llm_stress_test_results/` (blocked). Run `erh-gate` CLI in a
  scratch GH Actions run; confirm pipeline fails on high divergence. Deploy sidecar manifest
  to a local kind/minikube; app reaches engine over `localhost:50051`.
- **Phase 2:** Point IAM adapter at a test cloud account with a deliberately over-broad
  policy; confirm it is flagged as an ethical prime and the audit blocks.
- **Phase 3:** Replay a log fixture with an anomalous user (off-hours bulk download);
  confirm risk score rises and the deviation trajectory renders in the dashboard.
- **Regression:** existing suites stay green — `erh-security-app/backend` (11 tests),
  `simulation/app.py` import check, frontend `typecheck/build/lint`.

---

## Risks / Notes

- **Hybrid boundary:** Go↔Python adds a serialization seam; keep `erh_engine` the single
  source of algorithm truth — Go services must never re-implement scoring.
- **Live integrations need credentials** (LLM keys, cloud IAM read roles, SIEM access);
  every adapter ships a mock/fixture fallback so the system runs without secrets in CI.
- **Latency:** gRPC for the sidecar/proxy hot path; REST for batch/CI. Batch large IAM/UEBA
  evaluations to amortize engine cost.
- Scope is large; phases are independently shippable — Phase 0 unblocks everything.
