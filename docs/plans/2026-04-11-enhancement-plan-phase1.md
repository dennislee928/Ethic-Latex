# Enhancement Plan Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Land the first stabilization tranche from `docs/ENHANCEMENT_PLAN.md` by fixing confirmed backend defects, repairing the broken security frontend API contract, and aligning nearby dependency, CI, and status docs.

**Architecture:** Keep the scope narrow and repository-grounded. Stabilize the ERH security backend first with regression tests, then repair the dependent frontend contract, then update the minimum surrounding files that were directly preventing verification or misleading maintainers.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, pytest, Next.js, TypeScript, Streamlit, GitHub Actions

---

### Task 1: Lock in backend regressions with tests

**Files:**
- Create: `erh-security-app/backend/tests/conftest.py`
- Create: `erh-security-app/backend/tests/test_config.py`
- Create: `erh-security-app/backend/tests/test_verify_router.py`
- Create: `erh-security-app/backend/tests/test_simulate_router.py`

**Intent:**
- Reproduce the broken `verify_rule_by_id` flow.
- Reproduce the need for a session-factory based simulation task.
- Establish a local SQLite-backed backend test harness.

### Task 2: Make backend import and local DB behavior sane

**Files:**
- Modify: `erh-security-app/backend/app/config.py`
- Modify: `erh-security-app/backend/app/core/models.py`
- Modify: `erh-security-app/backend/app/main.py`

**Intent:**
- Default local development to SQLite instead of an implicit PostgreSQL dependency.
- Make JSON/JSONB columns portable across SQLite and PostgreSQL.
- Remove the `settings` name collision in `app.main`.

### Task 3: Fix backend route and background-task behavior

**Files:**
- Modify: `erh-security-app/backend/app/routers/verify.py`
- Modify: `erh-security-app/backend/app/routers/simulate.py`

**Intent:**
- Share verification logic through a helper that accepts raw LaTeX content.
- Make `verify_rule_by_id` call the shared helper correctly.
- Make simulation background tasks own their SQLAlchemy session lifecycle.

### Task 4: Repair the dependent frontend and utility path

**Files:**
- Modify: `erh-security-app/frontend/src/lib/api.ts`
- Modify: `simulation/app.py`

**Intent:**
- Add the missing `HealthMonitorResponse` and `getHealth()` exports.
- Fix the Streamlit results browser path by importing `json`.

### Task 5: Align nearby support files

**Files:**
- Modify: `requirements.txt`
- Modify: `.github/workflows/erh_security_app.yml`
- Modify: `docs/IMPLEMENTATION_STATUS.md`
- Modify: `tests/test_summary.md`

**Intent:**
- Add the root dependency needed for backend router tests in the repo `.venv`.
- Remove the invalid `npm test` expectation from the security frontend workflow.
- Reduce stale documentation claims that contradict the current tree or checked-in test artifacts.
