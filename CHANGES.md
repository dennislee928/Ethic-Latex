# Security & Enhancement Changes

Changes implemented from the Project Audit Report (2026-04-12).
Each entry references the audit item ID and a short description.

---

## 2026-05-16 — Julia Migration Started

A new `julia/` package (`ERH.jl`) has been introduced on branch `feature-partialre-factor-via-julia` to replace compute-heavy Python components with Julia equivalents while keeping the Python path as the default for all production services.

The migration is organized into four phases:

- **Phase 1 (Mathematical Core):** Julia rewrites of the zeta function evaluator, ERH bound checker, ethical primes generator, and statistical analysis utilities, backed by `SpecialFunctions.jl`, `Primes.jl`, and `Distributions.jl`.
- **Phase 2 (Simulation Framework):** ABM simulator, social network engine, temporal ERH model, hybrid model, and fluid dynamics model, using `Agents.jl`, `Graphs.jl`, and `DifferentialEquations.jl`.
- **Phase 3 (Quantum Simulation):** Local state-vector simulation via `Yao.jl`, targeting 30x speedup over Qiskit Aer.
- **Phase 4 (Batch Scripts):** Julia replacements for Python batch and figure-generation scripts, with Python originals kept as fallback.

Package scaffold (`julia/Project.toml`, `julia/src/ERH.jl`) and the GitHub Actions CI workflow (`.github/workflows/julia_tests.yml`) are complete. Implementation agents are writing the phase source files in parallel. Python code is unchanged; the PyJulia bridge falls back to pure Python if Julia is not installed, ensuring no production impact.

---

## Phase 1 — Security & Stability (Implemented)

### [VUL-001] Hardcoded IBM Quantum Token Removed
- **Files changed**: `.env`, `.env.example`
- **Description**: Replaced the real IBM Quantum API token (`UI1XNZWF02oRqTqsjTDa6ObzCkB3ZKqQX-7nW1VLnzxR`) in `.env` with a placeholder. Added a prominent warning comment explaining that the file must not be committed and that any previously exposed token must be revoked immediately. Updated `.env.example` to clearly document all required environment variables.
- **Action required**: Revoke the exposed token via https://quantum.ibm.com/ and run `git rm --cached .env` to stop tracking it.

### [VUL-002] CORS Policy Restricted
- **Files changed**: `erh-security-app/backend/app/main.py`, `erh-security-app/backend/app/config.py`, `.env.example`
- **Description**: Replaced `allow_origins=["*"]` with a configurable list of trusted origins read from the `CORS_ALLOWED_ORIGINS` environment variable (default: `http://localhost:3000`). Disabled `allow_credentials` (was `True` with wildcard origin — an invalid combination per the spec). Restricted allowed methods and headers to those actually needed.

### [VUL-003] Authentication Stub with Ownership Enforcement
- **Files changed**: `erh-security-app/backend/app/deps.py`, `erh-security-app/backend/app/routers/rules.py`, `erh-security-app/backend/app/routers/settings.py`
- **Description**: Added `get_current_user_id()` FastAPI dependency that centralises user resolution. Removed all `# TODO: Get user_id` / `# TODO: Check ownership` stubs. Wired the dependency into all rules and settings endpoints so that queries are now filtered by `owner_id`. Added `REQUIRE_AUTH` environment variable: when set to `true`, requests without an `Authorization: Bearer` header receive a 401. Full JWT validation is deferred (see Deferred section below).

### [VUL-005] LaTeX Input Validation
- **Files changed**: `erh-security-app/backend/app/routers/verify.py`
- **Description**: Added `_validate_latex_input()` that enforces a 100 KB size limit and rejects content containing dangerous LaTeX commands (`\write18`, `\input`, `\include`, `\openin`, `\openout`, `\read`, `\catcode`, `\special`, `\csname`, `\immediate\write18`). Called before passing content to the downstream verifier.

### [VUL-007] Code Complexity Input Validation
- **Files changed**: `erh-security-app/backend/app/routers/analysis.py`
- **Description**: Added size limit (50 KB) and empty-content check to the `/complexity` endpoint. Requests exceeding the limit receive HTTP 400. Added debug-level logging for accepted requests.

### [VUL-009] Weak Default PostgreSQL Password Removed
- **Files changed**: `docker-compose.yml`, `.env.example`
- **Description**: Removed the `:-erh_password` fallback default so that `POSTGRES_PASSWORD` must be explicitly set in the environment. The backend service connection string was updated to match. `.env.example` now documents how to generate a strong password.

### [VUL-010] Jupyter Notebook Authentication Enabled
- **Files changed**: `docker-compose.yml`, `.env.example`
- **Description**: Replaced the empty `--NotebookApp.token=''` (authentication disabled) with `--NotebookApp.token=${JUPYTER_TOKEN}`, requiring a token for all notebook connections. `.env.example` documents how to generate a secure token.

### [VUL-011] HuggingFace Oracle Error Differentiation
- **Files changed**: `erh_core/core/oracle.py`
- **Description**: Split the single broad `except Exception` block into three handlers: `MemoryError` (logs as error with advice), `RuntimeError` (logs as error — GPU/CUDA issues), and a general catch-all (logs as warning with explicit note that the fallback value 0.0 is indistinguishable from a neutral ethical score).

### [ENH-001] Structured Logging in Real-Data Case Studies
- **Files changed**: `simulation/real_data/adult_income_case_study.py`, `simulation/real_data/exam_cheating_case_study.py`, `simulation/real_data/sexual_abuse_case_study.py`
- **Description**: Replaced all `print()` calls in `run_real_data_case_study()` entry points with `logger.info()` / `logger.error(exc_info=True)`. Added `logging.getLogger(__name__)` to each module. Error paths now include full traceback context via `exc_info=True`.

### [ENH-002] Structured Logging in Core Library
- **Files changed**: `erh_core/core/social_network.py`
- **Description**: Replaced the single `print("matplotlib not available for visualization")` call with `logger.warning(...)`. Added `logging.getLogger(__name__)` to the module.

---

## Phase 2 — Medium Severity (Implemented)

### [VUL-008] Dependency Version Upper Bounds Added
- **Files changed**: `requirements.txt`
- **Description**: Added upper-bound version constraints to all dependencies (e.g., `numpy>=1.24.0,<3.0.0`) to prevent automatic upgrades to major versions with unknown security posture. Added a comment recommending `pip-audit` in CI. `pyproject.toml` dependencies were left unchanged as they use looser constraints appropriate for a library distribution.

### [ENH-008] ERH Bound Check Parameter Validation
- **Files changed**: `erh_core/analysis/erh_checks.py`
- **Description**: Replaced silent `None` return in `check_erh_bound()` with explicit `ValueError` raises. Added validation for: `None` inputs, shape mismatch between `E_x` and `x_values`, `C <= 0`, `epsilon < 0`, `allowed_violation_rate` outside `[0, 1]`, and `slack_factor <= 0`. Callers that relied on `None`-returning silent failures will now receive clear error messages.

---

## Deferred — Requires Infrastructure

### [VUL-003] Full JWT Authentication
- **Reason**: Requires new infrastructure: `User` and `Role` database models, password hashing (bcrypt), a `/auth/login` endpoint, JWT signing keys, and a secrets management strategy. The auth stub (`get_current_user_id()`) and `REQUIRE_AUTH` env var are in place to make the gap visible and auditable.

### [VUL-006] HTTP-Only Cookie Token Storage
- **Reason**: Requires completing JWT authentication first, then migrating the frontend (`frontend/src/store/authStore.ts`) from `localStorage` to HTTP-only cookies. Also requires CSRF token middleware on the FastAPI side.

### [FEAT-001] Multi-Tenancy / RBAC
- **Reason**: Requires `Tenant`, `User`, and `Role` models, database migrations, permission decorators, and row-level security in all queries.

### [FEAT-002] Web-Based Simulation Dashboard
- **Reason**: Requires WebSocket infrastructure, background task queue (Celery or similar), and significant new Next.js pages.

### [FEAT-003] Real-Time Error Monitoring
- **Reason**: Requires Prometheus client integration, a Grafana instance, and alerting system (PagerDuty/Slack).

### [FEAT-005] CI/CD for Empirical Validation
- **Reason**: Requires a time-series results store and access to real datasets in CI. Low risk — can be added to `.github/workflows/` once datasets are available in CI.

### [FEAT-006] Causal Inference Integration
- **Reason**: Requires the DoWhy library and significant framework extensions.

### [FEAT-007] Federated Learning
- **Reason**: Requires homomorphic encryption, differential privacy tooling, and distributed compute infrastructure.

### [ENH-003] Batch Simulation Timeout / Resource Limits
- **Reason**: `resource.setrlimit` is POSIX-only (not available on Windows) and may conflict with existing multiprocessing patterns. Needs design review before implementation.

### [ENH-004] Action Space Distribution Registry
- **Reason**: Non-breaking enhancement, but requires careful design to maintain reproducibility. Deferred to avoid scope creep.

### [ENH-007] Comprehensive Database Migration Strategy
- **Reason**: Requires Alembic migration coverage review, rollback testing in CI, and entrypoint changes. Deferred to avoid breaking existing dev workflows.
