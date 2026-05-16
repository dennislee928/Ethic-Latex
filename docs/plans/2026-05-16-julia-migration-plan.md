# Julia Migration Plan

**Date:** 2026-05-16  
**Branch:** feature-partialre-factor-via-julia  
**Goal:** Replace compute-heavy Python components with Julia without breaking production CI/CD.

---

## Implementation Status

*Last updated: 2026-05-16 by monitoring agent.*

| Phase | Component | Status | Files Created |
|---|---|---|---|
| 1 | Mathematical Core | In Progress | *(none yet — EthicalPrimes.jl, ZetaFunction.jl, ERHChecks.jl, ERHStatistics.jl pending)* |
| 2 | Simulation Framework | In Progress | *(none yet — ABMSimulator.jl, SocialNetwork.jl, TemporalERH.jl, HybridModel.jl, FluidModel.jl pending)* |
| 3 | Quantum Simulation | In Progress | *(none yet — QuantumSimulator.jl, QuantumWalk.jl pending)* |
| 4 | Batch Scripts | In Progress | *(none yet — run_simulation_batch.jl, generate_all_figures.jl pending)* |
| — | CI/CD Workflow | Complete | `.github/workflows/julia_tests.yml` |
| — | Package Scaffold | Complete | `julia/Project.toml`, `julia/src/ERH.jl` |

---

## Why Julia for This Project

This project's core is **mathematical/numerical computation** — exactly where Julia excels:

| Concern | Python Status | Julia Advantage |
|---|---|---|
| Zeta function evaluation | NumPy/SciPy loops | Native arbitrary-precision arithmetic, `SpecialFunctions.jl` |
| ERH bound checking | Pure Python math | 10–100× faster for tight numerical loops |
| Agent-based modeling | Custom Python classes | `Agents.jl` — production ABM framework with parallelism |
| Statistical analysis | scipy.stats | `Distributions.jl`, `HypothesisTests.jl` — same API, faster |
| Quantum simulation | Qiskit Aer (Python) | `Yao.jl` — orders of magnitude faster for local simulation |
| Figure generation | Matplotlib/Seaborn | `Makie.jl` / `CairoMakie.jl` — publication-quality, GPU-accelerated |
| Batch script runner | Python subprocess | Native Julia parallelism (`@distributed`, `Threads.@threads`) |

**Do NOT replace:** FastAPI backend, Next.js/React frontend, TypeScript SDK, Alembic migrations, CI/CD YAML structure (only add Julia steps).

---

## Migration Phases

### Phase 1 — Mathematical Core (Low Risk, High Value)

**Target files:**

| Python File | Lines | Replacement |
|---|---|---|
| `erh_core/analysis/zeta_function.py` | ~200 | `julia/src/ZetaFunction.jl` |
| `erh_core/analysis/erh_checks.py` | ~150 | `julia/src/ERHChecks.jl` |
| `erh_core/analysis/statistics.py` | ~180 | `julia/src/ERHStatistics.jl` |
| `erh_core/core/ethical_primes.py` | ~120 | `julia/src/EthicalPrimes.jl` |
| `erh_core/analysis/zeta_zeros_analysis.py` | ~160 | folded into `ZetaFunction.jl` |

**Why these first:** Pure math with no web/DB/UI dependencies. Zero production surface impact. Verified with existing Python test suite via `PyJulia`.

**How:**

1. Create `julia/` package at repo root:
   ```
   julia/
   ├── Project.toml          # Julia project file
   ├── Manifest.toml         # Locked dependencies
   └── src/
       ├── ERH.jl            # Main module (re-exports everything)
       ├── EthicalPrimes.jl
       ├── ZetaFunction.jl
       ├── ERHChecks.jl
       └── ERHStatistics.jl
   ```

2. Expose Julia functions to Python via `PyJulia` (`julia` pip package):
   ```python
   # erh_core/analysis/zeta_function.py  (updated shim)
   try:
       from julia import ERH as _jl
       def ethical_zeta(s, primes):
           return _jl.ethical_zeta(s, primes)
   except ImportError:
       # fall back to pure-Python implementation
       from ._zeta_pure import ethical_zeta
   ```

3. Fallback to pure Python if Julia is not installed — production never breaks.

**Julia packages needed:**
```toml
[deps]
SpecialFunctions = "276daf66-3868-5448-9aa4-cd146d93841b"
Primes = "27ebfcd6-29c5-5fa9-bf4e-3b359b1bc57d"
Statistics = "10745b16-79ce-11e8-11f9-7d13ad32a3b1"
HypothesisTests = "09f84164-cd44-5f33-b23f-e6b0d136a0d5"
Distributions = "31c24e10-a181-5473-b8eb-7969acd0382f"
```

---

### Phase 2 — Simulation Framework (Medium Risk, High Value)

**Target files:**

| Python File | Lines | Replacement |
|---|---|---|
| `erh_core/core/abm_simulator.py` | ~300 | `julia/src/ABMSimulator.jl` using `Agents.jl` |
| `erh_core/core/social_network.py` | ~250 | `julia/src/SocialNetwork.jl` using `Graphs.jl` |
| `erh_core/core/temporal_erh.py` | ~200 | `julia/src/TemporalERH.jl` |
| `erh_core/core/hybrid_model.py` | ~180 | `julia/src/HybridModel.jl` |
| `erh_core/analysis/fluid_model.py` | ~150 | `julia/src/FluidModel.jl` using `DifferentialEquations.jl` |
| `erh_core/analysis/opinion_dynamics.py` | ~130 | folded into `SocialNetwork.jl` |

**Why these next:** The ABM simulator and network analysis are the biggest compute bottlenecks. `Agents.jl` natively supports parallel execution across cores and has a well-tested spatial graph scheduler.

**Julia packages needed:**
```toml
Agents = "46ada45e-f475-11e8-01d0-f70cc89e6671"
Graphs = "86223c79-3864-5bf0-83f7-82e725a168b3"
DifferentialEquations = "0c46a032-eb83-5123-abaf-570d42b7fbaa"
```

**Integration approach for the Streamlit app (`simulation/app.py`):**

Run Julia as a sidecar HTTP microservice using `Oxygen.jl`:

```julia
# julia/src/server.jl
using Oxygen, HTTP, JSON3
using ERH

@get "/simulate" function(req::HTTP.Request)
    params = JSON3.read(req.body)
    result = ABMSimulator.run(params)
    return json(result)
end

serve(; host="127.0.0.1", port=8765)
```

Then in `simulation/app.py`, add a config flag:
```python
USE_JULIA_BACKEND = os.getenv("ERH_JULIA_BACKEND", "false").lower() == "true"
```

This keeps the Python path as default; Julia path activates via env var.

---

### Phase 3 — Quantum Simulation (Optional, High Value)

**Target files:**

| Python File | Lines | Replacement |
|---|---|---|
| `simulation/quantum/simulator.py` | ~200 | `julia/src/QuantumSimulator.jl` using `Yao.jl` |
| `simulation/quantum/quantum_walk.py` | ~150 | `julia/src/QuantumWalk.jl` |

**Keep in Python (do not replace):**
- `simulation/quantum/cloud.py` — IBM Quantum Runtime uses `qiskit-ibm-runtime`, which has no Julia equivalent for cloud job submission.
- `simulation/quantum/interface.py` — thin adapter layer, keep it.
- `simulation/quantum/worker.py` — keep Python for distributed worker orchestration.

**Julia packages needed:**
```toml
Yao = "5872b779-8223-5990-8dd0-5abbb0748c8e"
YaoArrayRegister = "e600142f-9330-5003-9dd5-7fb2ee2f5651"
```

**Benchmark expectation:** Yao.jl simulation of a 20-qubit circuit runs ~30× faster than Qiskit Aer (CPU) for equivalent state-vector simulation.

---

### Phase 4 — Batch Scripts & Figure Generation (Low Risk)

**Target files:**

| Python Script | Replacement |
|---|---|
| `scripts/run_simulation_batch.py` | `julia/scripts/run_simulation_batch.jl` |
| `scripts/run_phase_transition_exp.py` | `julia/scripts/run_phase_transition.jl` |
| `scripts/run_empirical_validation.py` | `julia/scripts/run_empirical_validation.jl` |
| `scripts/generate_all_figures.py` | `julia/scripts/generate_all_figures.jl` using `CairoMakie.jl` |
| `scripts/alpha_stability_report.py` | `julia/scripts/alpha_stability_report.jl` |
| `scripts/calculate_alpha_comparison.py` | `julia/scripts/calculate_alpha_comparison.jl` |

**Julia packages needed:**
```toml
CairoMakie = "13f3f980-e62b-5c42-98c6-ff1f3baf88f0"
DataFrames = "a93c6f00-e57d-5684-b466-afe8fa294f15"
CSV = "336ed68f-0bac-2571-8ef2-6bf8f2f3de23"
GLM = "38e38edf-8417-5370-95a0-9cbb8c7f171a"
```

**Why:** Pure script replacement — no production surface. Old Python scripts remain as fallback. Run Julia scripts alongside Python in CI to verify output parity before removing Python versions.

---

## What NOT to Replace

| Component | Reason |
|---|---|
| `erh-security-app/backend/` (FastAPI) | No production Julia HTTP framework matches FastAPI + SQLAlchemy + Alembic maturity |
| `erh-security-app/frontend/` (Next.js) | Frontend — Julia has no browser target |
| `js-sdk/` (TypeScript) | npm ecosystem requirement |
| `simulation/real_data/*.py` | HuggingFace, pandas DataFrames — Python ecosystem is better here |
| `simulation/api/` (FastAPI schemas) | Tied to Python backend |
| `tests/*.py` (pytest suite) | Keep Python tests; add Julia tests separately |
| `.github/workflows/*.yml` | Keep YAML; only add new Julia steps |
| Alembic migrations | SQLAlchemy/Alembic have no Julia equivalent |

---

## Integration Strategy

### Option A — PyJulia (Recommended for Phase 1 & 2)

Install `julia` Python package. Call Julia functions directly from Python with zero subprocess overhead:

```bash
pip install julia
python -c "import julia; julia.install()"
```

```python
from julia import Main
Main.include("julia/src/ERH.jl")
result = Main.ERH.ethical_zeta(complex(0.5, 14.13), primes)
```

**Pros:** No IPC overhead, shares memory for arrays via PyCall.jl.  
**Cons:** Julia startup time (~5s first call, then fast). Mitigate with `--project` sysimage.

### Option B — Julia HTTP Microservice (Recommended for Phase 2 & 3)

Run Julia as a sidecar process. FastAPI/Streamlit call it via `httpx`:

```python
async with httpx.AsyncClient() as client:
    r = await client.post("http://localhost:8765/simulate", json=params)
```

**Pros:** Full process isolation, language-agnostic JSON contract.  
**Cons:** JSON serialization overhead, requires starting Julia process separately.

### Option C — Julia CLI subprocess (Simplest, Phase 4)

```python
import subprocess, json
result = subprocess.run(
    ["julia", "--project=julia", "julia/scripts/run_phase_transition.jl", "--params", json.dumps(params)],
    capture_output=True
)
```

**Pros:** Zero integration code, clear separation.  
**Cons:** 5–10s Julia startup per call — only suitable for batch scripts.

**Recommendation:** Use Option A for library functions (Phases 1–2), Option B for the simulation server, Option C for one-shot batch scripts.

---

## CI/CD Changes

### New workflow: `.github/workflows/julia_tests.yml`

```yaml
name: Julia Tests

on:
  push:
    paths:
      - 'julia/**'
      - '.github/workflows/julia_tests.yml'
  pull_request:
    paths:
      - 'julia/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: julia-actions/setup-julia@v2
        with:
          version: '1.11'

      - uses: julia-actions/cache@v2

      - name: Install Julia dependencies
        run: |
          julia --project=julia -e 'using Pkg; Pkg.instantiate()'

      - name: Run Julia tests
        run: |
          julia --project=julia -e 'using Pkg; Pkg.test("ERH")'
```

### Updates to existing workflows

**`simulation.yml`** — add optional Julia backend smoke test:
```yaml
- name: Julia backend smoke test (optional)
  if: env.JULIA_AVAILABLE == 'true'
  run: |
    julia --project=julia julia/scripts/run_simulation_batch.jl --smoke
  continue-on-error: true   # non-blocking until Phase 2 is complete
```

**`sdk_python.yml`** — add PyJulia bridge test:
```yaml
- uses: julia-actions/setup-julia@v2
  with:
    version: '1.11'
- name: Test PyJulia bridge
  run: |
    pip install julia
    python -c "import julia; julia.install(); from julia import ERH; print(ERH.version())"
  continue-on-error: true   # non-blocking in Phase 1
```

---

## Directory Layout (Final State)

```
Ethic-Latex/
├── julia/                        # NEW — Julia package
│   ├── Project.toml
│   ├── Manifest.toml
│   ├── src/
│   │   ├── ERH.jl                # Main module entry
│   │   ├── EthicalPrimes.jl      # Phase 1
│   │   ├── ZetaFunction.jl       # Phase 1
│   │   ├── ERHChecks.jl          # Phase 1
│   │   ├── ERHStatistics.jl      # Phase 1
│   │   ├── ABMSimulator.jl       # Phase 2
│   │   ├── SocialNetwork.jl      # Phase 2
│   │   ├── TemporalERH.jl        # Phase 2
│   │   ├── HybridModel.jl        # Phase 2
│   │   ├── FluidModel.jl         # Phase 2
│   │   ├── QuantumSimulator.jl   # Phase 3
│   │   ├── QuantumWalk.jl        # Phase 3
│   │   └── server.jl             # Phase 2 — Oxygen.jl HTTP microservice
│   ├── scripts/                  # Phase 4 — batch script replacements
│   │   ├── run_simulation_batch.jl
│   │   ├── run_phase_transition.jl
│   │   ├── run_empirical_validation.jl
│   │   ├── generate_all_figures.jl
│   │   └── alpha_stability_report.jl
│   └── test/
│       ├── runtests.jl           # Julia test entry
│       ├── test_zeta_function.jl
│       ├── test_erh_checks.jl
│       ├── test_ethical_primes.jl
│       └── test_abm_simulator.jl
```

---

## Parity Verification Strategy

Before removing any Python file, run a parity check:

```python
# tests/test_julia_parity.py  (new file)
import pytest
from julia import ERH as jl_ERH
from erh_core.analysis.zeta_function import ethical_zeta as py_zeta

@pytest.mark.julia
def test_zeta_parity():
    """Julia and Python zeta functions agree to 6 decimal places."""
    for s in [complex(0.5, t) for t in [14.13, 21.02, 25.01]]:
        py = py_zeta(s, primes=[2, 3, 5, 7, 11])
        jl = jl_ERH.ethical_zeta(s, [2, 3, 5, 7, 11])
        assert abs(py - jl) < 1e-6, f"Divergence at s={s}: py={py}, jl={jl}"
```

Run parity tests in CI before removing the Python implementation. Only remove the Python file after 3 consecutive green CI runs.

---

## Rollout Order & Timeline

| Phase | Components | Risk | Estimated Effort | Prerequisite |
|---|---|---|---|---|
| **1** | Math core (zeta, ERH checks, primes, stats) | Low | 1–2 weeks | None |
| **2** | ABM simulator, social network, temporal, fluid | Medium | 2–3 weeks | Phase 1 complete |
| **3** | Quantum local simulator | Low-Medium | 1 week | Phase 1 complete |
| **4** | Batch scripts, figure generation | Low | 1 week | Phase 2 complete |

**Total estimated effort:** 5–7 weeks of part-time work.

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Julia startup latency in CI | Use `julia-actions/cache@v2` to cache compiled sysimage |
| PyJulia incompatibility with Python 3.10 | Pin `julia>=0.6.1`; test in CI before merging |
| Numeric divergence between Julia and Python | Parity tests with tolerance thresholds (see above) |
| `Agents.jl` API differences from Python ABM | Keep Python ABM running until parity tests pass |
| Docker image size increase | Use multi-stage Dockerfile; Julia layer only in simulation stage |
| Team unfamiliarity with Julia | Start with Phase 1 (pure math) — Julia syntax is close to MATLAB/Python for numerics |

---

## Quick Start for Implementation

```bash
# 1. Install Julia 1.11+
curl -fsSL https://install.julialang.org | sh

# 2. Create the Julia package
mkdir -p julia/src julia/test julia/scripts
cd julia

# 3. Initialize Project.toml
julia -e 'using Pkg; Pkg.generate(".")'

# 4. Add dependencies (Phase 1)
julia --project=. -e '
using Pkg
Pkg.add([
    "SpecialFunctions",
    "Primes",
    "Statistics",
    "Distributions",
    "HypothesisTests",
])
'

# 5. Install PyJulia bridge
pip install julia
python -c "import julia; julia.install()"
```

Then implement `julia/src/EthicalPrimes.jl` first (smallest file, clearest spec from `erh_core/core/ethical_primes.py`) and run the parity test to validate the approach before proceeding to larger files.
