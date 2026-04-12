# Enhancement Plan Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Land the first stabilization tranche from `docs/ENHANCEMENT_PLAN.md` by fixing confirmed backend defects, repairing the broken security frontend API contract, and aligning nearby dependency, CI, and status docs.

**Architecture:** Keep the scope narrow and repository-grounded. Stabilize the ERH security backend first with regression tests, then repair the dependent frontend contract, then update the minimum surrounding files that were directly preventing verification or misleading maintainers.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, pytest, Next.js, TypeScript, Streamlit, GitHub Actions

---

## Progress Update (2026-04-12)

**Status:** Phase 1 stabilization tranche implemented and verified for the security backend/frontend surfaces.

**Completed in repository:**
- Backend regression harness added with SQLite-backed tests for config, verify route, simulation background-task session ownership, and simulation create/status/results route flow.
- Local backend defaults switched to SQLite, `app.main` naming collision removed, and JSON columns made portable across SQLite/PostgreSQL.
- Verification logic now flows through a shared helper and `POST /api/v1/verify/rule/{id}` is covered by a smoke test.
- Simulation background tasks now create and close their own SQLAlchemy session.
- Next.js security frontend now exports `HealthMonitorResponse` and `getHealth()`.
- `simulation/app.py` imports `json`, the root environment includes `SQLAlchemy` and `pydantic-settings`, and the security workflow no longer calls undefined `npm test`.
- Nearby stale status language in documentation was reduced.

**Verification run on 2026-04-12:**
- `erh-security-app/backend/tests`: `11 passed`
- `erh-security-app/frontend`: `npm run build` passed
- `erh-security-app/frontend`: `npm run lint` passed
- `simulation/app.py`: `py_compile` passed

**Follow-up completed after verification:**
- Replaced deprecated `datetime.utcnow()` usage in the security backend with a shared UTC helper to reduce warning noise in tests.
- Added an explicit Next.js security frontend typecheck step (`tsc --noEmit`) so the CI workflow now checks build, typecheck, and lint separately.
- Made the backend SQLite test database path process-specific so concurrent verification runs do not collide on the same temp database file.
- Added a dated verified-surfaces snapshot and architecture map to `README.md` and `docs/IMPLEMENTATION_STATUS.md` so repository-facing docs now match the latest stabilization evidence.
- Updated `erh-security-app/README.md`, `docs/QUICKSTART.md`, and `docs/INSTALL.md` so run/install guidance explicitly separates the verified security app path from the broader research/simulation path.

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
