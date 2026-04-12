# QA Test Report — CHANGES.md Audit (2026-04-12)

**Project:** Ethic-Latex  
**Branch:** dev  
**Last commit:** d856a2c (update : rules-mdc)  
**Verified by:** Claude Code automated QA  
**Date:** 2026-04-12

---

## 1. Static Analysis — Syntax Checks

All Python files mentioned in CHANGES.md were compiled with `python3 -m py_compile`.

| File | Status |
|---|---|
| `erh-security-app/backend/app/main.py` | PASS |
| `erh-security-app/backend/app/config.py` | PASS |
| `erh-security-app/backend/app/deps.py` | PASS |
| `erh-security-app/backend/app/routers/verify.py` | PASS |
| `erh-security-app/backend/app/routers/analysis.py` | PASS |
| `erh-security-app/backend/app/routers/rules.py` | PASS |
| `erh-security-app/backend/app/routers/settings.py` | PASS |
| `erh_core/core/oracle.py` | PASS |
| `erh_core/core/social_network.py` | PASS |
| `erh_core/analysis/erh_checks.py` | PASS |
| `simulation/real_data/adult_income_case_study.py` | PASS |
| `simulation/real_data/exam_cheating_case_study.py` | PASS |
| `simulation/real_data/sexual_abuse_case_study.py` | PASS |

**All syntax checks: PASS (13/13)**

---

## 2. Test Suite Execution

```
python3 -m pytest tests/ -q
```

**Results:** 88 passed, 1 failed, 6 skipped, 28 warnings — 11.54s

### Failure: `tests/test_simulator_ising.py::test_calculate_von_neumann_entropy_density_matrix`

```
assert 3.453877639491069e-14 == 0.0
AssertionError
```

**Root cause:** Floating-point precision. The test asserts exact equality with `0.0` for the von Neumann entropy of a pure state. NumPy's matrix eigenvalue decomposition introduces a tiny numerical residual (~3.5e-14), which is mathematically correct behaviour.

**Relation to CHANGES.md:** This test file was last modified in commit `5298de9` (predates the current audit cycle). It is **NOT introduced or broken by any change in CHANGES.md**.

**Suggested fix (low priority):** Change the assertion in `tests/test_simulator_ising.py` line 183 to use a tolerance:
```python
assert s_pure < 1e-12  # pure state: entropy is effectively 0
```
or use `pytest.approx`:
```python
assert s_pure == pytest.approx(0.0, abs=1e-12)
```

**Verdict:** Pre-existing test failure, unrelated to the audited changes. All 88 other tests pass.

---

## 3. Security Verification

### 3a. VUL-001 — Hardcoded IBM Quantum Token

- Searched all `.py`, `.js`, `.ts`, `.json`, `.yml`, `.yaml`, `.txt` files (excluding `.env`) for token `UI1XNZWF02oRqTqsjTDa6ObzCkB3ZKqQX`.
- **Result: PASS** — Token not found in any tracked non-.env file.
- The `.env` file contains only the placeholder `IBM_QUANTUM_TOKEN=your_ibm_quantum_token_here`.

### 3b. VUL-002 — CORS Policy

- `erh-security-app/backend/app/main.py`: CORS `allow_origins` is built from `app_settings.cors_allowed_origins.split(",")`, which is read from the `CORS_ALLOWED_ORIGINS` environment variable (default: `http://localhost:3000`).
- `allow_credentials` is set to `False`.
- Methods restricted to: `GET, POST, PUT, DELETE, OPTIONS`.
- Headers restricted to: `Content-Type, Authorization`.
- **Result: PASS** — CORS is no longer hardcoded; uses env var correctly.

**Warning:** `simulation/api/main.py` (the older simulation API, not part of CHANGES.md scope) still has `allow_origins=["*"]` with `allow_credentials=True`. This was **not** changed in the current audit cycle, but should be addressed in a follow-up.

### 3c. VUL-005 — LaTeX Input Validation

- `_validate_latex_input()` is defined in `verify.py` and called inside `_verify_latex_content()` before any downstream processing.
- Enforces 100 KB size limit via `len(latex_content.encode("utf-8")) > _MAX_LATEX_BYTES`.
- Rejects the following commands (case-insensitive): `\immediate\write18`, `\write18`, `\input`, `\include`, `\openin`, `\openout`, `\read`, `\catcode`, `\special`, `\csname`.
- Functional tests confirm all dangerous commands are rejected (HTTP 400) and valid LaTeX is accepted.
- **Result: PASS**

---

## 4. Import Checks

All changed modules were imported cleanly in the appropriate working directory:

| Module | Command | Status |
|---|---|---|
| `erh_core.analysis.erh_checks` | `python3 -c "from erh_core.analysis.erh_checks import check_erh_bound"` | PASS |
| `erh_core.core.oracle` | `python3 -c "from erh_core.core.oracle import HuggingFaceEthicalOracle"` | PASS |
| `erh_core.core.social_network` | `python3 -c "from erh_core.core.social_network import SocialNetwork"` | PASS |
| `simulation.real_data.adult_income_case_study` | `python3 -c "from simulation.real_data.adult_income_case_study import run_real_data_case_study"` | PASS |
| `simulation.real_data.exam_cheating_case_study` | `python3 -c "from simulation.real_data.exam_cheating_case_study import run_real_data_case_study"` | PASS |
| `simulation.real_data.sexual_abuse_case_study` | `python3 -c "from simulation.real_data.sexual_abuse_case_study import run_real_data_case_study"` | PASS |
| `app.config` (from `erh-security-app/backend/`) | `python3 -c "from app.config import get_settings"` | PASS |

**WARNING — Import failure when run from project root:** When `sys.path` includes `erh-security-app/backend` and the current working directory is the project root, the pydantic `Settings` model raises a `ValidationError`:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
ibm_quantum_token
  Extra inputs are not permitted [type=extra_forbidden, ...]
```

**Root cause:** The `.env` file at the project root contains `IBM_QUANTUM_TOKEN=...`, but the backend `Settings` model (in `config.py`) does not declare this field and `SettingsConfigDict` does not set `extra="ignore"`. The backend correctly loads its own `.env` when run from `erh-security-app/backend/`, but if the app is ever started from the project root (e.g., in some CI pipelines or Docker entrypoints), it will fail to start.

**Suggested fix:** Add `extra="ignore"` to the `SettingsConfigDict` in `config.py`:
```python
model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",   # <-- add this
)
```

---

## 5. Change-by-Change Verification

| Change ID | Description | Verified | Status |
|---|---|---|---|
| VUL-001 | Hardcoded IBM token removed from `.env` | Token absent from all non-.env files | PASS |
| VUL-002 | CORS reads `CORS_ALLOWED_ORIGINS` env var | Confirmed in `main.py`; credentials disabled | PASS |
| VUL-003 | Auth stub with ownership enforcement | `get_current_user_id()` wired into all rules/settings endpoints; `REQUIRE_AUTH` flag works | PASS |
| VUL-005 | LaTeX input validation | `_validate_latex_input()` called in `_verify_latex_content()`; 10 dangerous commands blocked; 100 KB limit enforced | PASS |
| VUL-007 | Code complexity input validation | 50 KB limit and empty-content check present in `/complexity` endpoint | PASS |
| VUL-009 | Weak default PostgreSQL password removed | `docker-compose.yml` uses `${POSTGRES_PASSWORD}` with no fallback `:-erh_password` default | PASS |
| VUL-010 | Jupyter notebook auth enabled | `docker-compose.yml` uses `--NotebookApp.token=${JUPYTER_TOKEN}` | PASS |
| VUL-011 | HuggingFace oracle error differentiation | Three separate handlers: `MemoryError`, `RuntimeError`, and catch-all `Exception` with explicit fallback warning | PASS |
| ENH-001 | Structured logging in real-data case studies | All three case study files use `logger.info()`/`logger.error(exc_info=True)`; no `print()` calls remain | PASS |
| ENH-002 | Structured logging in `social_network.py` | `logger.warning()` replaces `print()`; `logger = logging.getLogger(__name__)` added | PASS |
| VUL-008 | Dependency upper bounds in `requirements.txt` | All dependencies have `<X.0.0` upper bounds; `pip-audit` comment added | PASS |
| ENH-008 | ERH bound check parameter validation | `ValueError` raised for `None` inputs, shape mismatch, `C<=0`, `epsilon<0`, `allowed_violation_rate` out of range, `slack_factor<=0`; confirmed by functional tests | PASS |

---

## 6. Logic Review Notes

- **VUL-003 auth stub is clearly documented** as a stub returning `user_id=1`. The `REQUIRE_AUTH=true` mode correctly blocks unauthenticated requests but does not validate JWT tokens (this is flagged as deferred infrastructure). No logic errors found.
- **ENH-008 `check_erh_bound`**: The validation guards are comprehensive and correctly placed before array operations. The valid-path logic is unchanged from the pre-audit version and produces correct results on test inputs.
- **VUL-005 dangerous command matching**: Uses `.lower()` for case-insensitive comparison on both the command list and the content. This is correct. `\immediate\write18` is listed first (though ordering doesn't affect correctness since all commands are checked independently), and the compound form is correctly detected.

---

## 7. Warnings (Non-Blocking)

1. **Pre-existing test failure** (`test_simulator_ising.py:183`): Numerical precision issue, unrelated to audited changes. Fix: use `pytest.approx` or `abs` tolerance.

2. **`Settings` model lacks `extra="ignore"`** (`erh-security-app/backend/app/config.py`): Will raise `ValidationError` if the app is started from a directory where `.env` contains `IBM_QUANTUM_TOKEN`. Harmless when started from the backend directory, but fragile for Docker deployments. Fix: add `extra="ignore"` to `SettingsConfigDict`.

3. **`simulation/api/main.py` still has `allow_origins=["*"]`**: This was out of scope for the current audit, but is a security concern if the simulation API is exposed publicly.

4. **Qiskit deprecation warnings** (28 warnings): Multiple `qiskit 2.1` API deprecations for classes that will be removed in Qiskit 3.0. Non-blocking today but should be addressed before Qiskit 3.0 upgrade.

---

## Overall Verdict

> **PASS WITH WARNINGS**

All changes described in CHANGES.md are correctly implemented, syntactically valid, and functionally verified. No regressions were introduced in the 88 passing tests. The one failing test is a pre-existing numerical precision issue unrelated to this change set. Two warnings (Settings `extra="ignore"` and the `simulation/api/main.py` CORS wildcard) should be remediated in a follow-up PR.
