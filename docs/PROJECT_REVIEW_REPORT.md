# Project Review Report

Date: 2026-04-11
Repository: `Ethic-Latex`

## Scope

This review covered the repository structure, packaging setup, core Python modules, simulation surfaces, the ERH security app, the frontends, CI workflows, tests, and checked-in generated artifacts.

## Verification Snapshot

- `./.venv/bin/pytest -q tests/test_sdk.py` passed: `2 passed in 5.11s`.
- `PYTHONPATH=. ./.venv/bin/pytest -q erh-security-app/backend/tests/test_analysis_router.py erh-security-app/backend/tests/test_ingestion_router.py erh-security-app/backend/tests/test_mapping.py` failed during collection because `sqlalchemy` is not installed in the root `.venv`.
- The repository currently mixes at least two Python runtimes in-tree: `./.venv/bin/python` is `3.14.2`, and `./.venv_erh/bin/python` is `3.9.6`.

## Executive Summary

The project has strong breadth and a substantial amount of implemented research code, but it is carrying too many product surfaces and too much checked-in generated state for the current level of operational discipline. The highest-risk problems are concentrated in the ERH security app, where there are runtime bugs in verification and simulation task handling, and in the Next.js frontend, which appears unable to compile against its own API helper module. Documentation and repository hygiene are also materially out of sync with the actual codebase.

## Strengths

- The repo contains a meaningful core library split, with `erh_core` clearly intended as the canonical implementation surface.
- The SDK smoke tests currently pass.
- There is evidence of serious experimentation effort: notebooks, simulation outputs, CI workflows, deployment docs, and multiple UX surfaces.
- The security app has useful route separation and a reasonable initial domain model for actions, judgments, rules, and reports.

## Findings

### High

1. `verify_rule_by_id` is broken at runtime.

- File: `erh-security-app/backend/app/routers/verify.py`
- Evidence: lines 92-102 call `verify_rule(rule.content, rule_id=rule_id, db=db)`, but `verify_rule()` expects a `VerifyRequest` object and immediately accesses `request.latex_content` on line 35.
- Impact: `POST /api/v1/verify/rule/{rule_id}` will raise an attribute error instead of verifying an existing rule.

2. The simulation background task uses a request-scoped SQLAlchemy session after the request has finished.

- File: `erh-security-app/backend/app/routers/simulate.py`
- Evidence: `create_simulation()` injects `db: Session = Depends(get_db)` and passes that live session into `background_tasks.add_task(...)` on lines 106-114. The dependency comes from `get_db_session()` in `erh-security-app/backend/app/core/db.py`, which closes the session in `finally`.
- Impact: background jobs can run with a closed or invalid session, causing intermittent failures or state corruption when marking simulations running, completed, or failed.

3. The Next.js security frontend has a compile-time API contract break.

- Files: `erh-security-app/frontend/src/pages/index.tsx`, `erh-security-app/frontend/src/lib/api.ts`
- Evidence: `index.tsx` imports `HealthMonitorResponse` and `getHealth` on lines 7-14 and calls `getHealth(judgeType)` on line 55, but `lib/api.ts` only exports `JudgeType`, `AnalysisSummary`, `AnalysisCurves`, `HeatmapResponse`, `getSummary`, `getCurves`, and `getHeatmap`.
- Impact: the security frontend should fail TypeScript compilation or at minimum fail module resolution for the health-monitor path.

### Medium

4. CI does not provide a trustworthy signal for the security frontend.

- Files: `.github/workflows/erh_security_app.yml`, `erh-security-app/frontend/package.json`
- Evidence: the workflow runs `npm test` on lines 87-89, but the package has no `test` script; it only defines `dev`, `build`, `start`, and `lint` on lines 5-9.
- Impact: frontend validation is weaker than it appears, and the workflow tolerates this anyway with `continue-on-error: true`.

5. Documentation claims completion for modules that do not exist at the documented paths.

- File: `docs/IMPLEMENTATION_STATUS.md`
- Evidence: lines 14, 30, 47, 61, 62, 79, 94, and 108 reference `simulation/...` modules that are not present in the repository. Those capabilities appear to have moved into `erh_core/...` or were never reconciled after refactors.
- Impact: maintainers and contributors cannot trust status docs when planning work or debugging regressions.

6. Checked-in test outputs contradict the checked-in test summary.

- Files: `tests/test_summary.md`, `tests/notebooks/output/output.xml`
- Evidence: `tests/test_summary.md` says "All tests should pass" on line 136, but `tests/notebooks/output/output.xml` records `pass="5" fail="2"` for notebook tests and explicitly shows failures around lines 1393-1414.
- Impact: the repository is preserving stale success claims alongside stale failure artifacts.

7. The repository is heavily polluted with generated, local, and editor-specific material.

- Evidence:
- `git ls-files` reports 2,980 tracked files.
- Tracked non-source directories include `.venv_erh/` with 657 files, `docs/_build/` with 86 files, `js-sdk/node_modules/` with 152 files, `.claude/` with 1,306 files, and `.cursor/` with 306 files.
- On disk, `.venv_erh` is about `712M`, `.worktrees` is about `750M`, `js-sdk/node_modules` is about `23M`, and `docs/_build` is about `12M`.
- `.gitignore` does attempt to ignore some of these paths, but they are already tracked, so the ignore file is no longer effective for repository cleanup.
- Impact: clone size, review noise, CI churn, accidental leakage of local/editor state, and degraded maintainability.

8. The architecture is fragmented across too many overlapping entry points.

- Examples:
- Root Python package via `pyproject.toml`
- `simulation/api/main.py` FastAPI app
- `simulation/app.py` Streamlit app
- root Vite frontend in `frontend/`
- security Next.js frontend in `erh-security-app/frontend/`
- security Vite frontend in `erh-security-app/frontend-vite/`
- JS SDK in `js-sdk/`
- Impact: it is unclear which surfaces are authoritative, production-ready, experimental, or abandoned. README line 52 says `erh_core` is the "Single Source of Truth", but the repo structure no longer feels single-surface in practice.

9. Dependency management is inconsistent across packaging surfaces.

- Files: `pyproject.toml`, `requirements.txt`, `erh-security-app/backend/requirements.txt`
- Evidence:
- `pyproject.toml` defines a minimal runtime dependency set for the package.
- `requirements.txt` mixes runtime, dev tools, notebooks, testing, streamlit, quantum, HuggingFace, and data tooling in one file.
- The backend has its own `requirements.txt`, including an editable install of the repo root.
- The root `.venv` lacked `sqlalchemy`, while backend tests depend on it.
- Impact: setup reproducibility is weak, and a "working environment" depends on which install path a developer happens to choose.

10. `simulation/app.py` contains an obvious runtime bug in the results browser.

- File: `simulation/app.py`
- Evidence: it calls `json.load(uploaded_file)` on line 203, but there is no `import json` in the file.
- Impact: the "Results Browser" mode will fail once a user uploads JSON files.

## Additional Notes

- The backend tests import from `app.main` rather than from an installable package. That works only because CI changes working directories. It is convenient for local iteration, but it reinforces that `erh-security-app` is not packaged as a reusable Python module.
- `simulation/api/main.py` and the security backend both expose overlapping HTTP concerns, which increases the risk of client drift.

## Recommended Priority Order

1. Fix the broken security app routes and background task session lifecycle.
2. Make the security frontend compile against a real API client contract.
3. Decide which backend and frontend surfaces are official.
4. Remove tracked generated/vendor/local state from Git.
5. Rebuild documentation from the surviving surfaces only.

## Bottom Line

The project has enough real implementation to justify a stabilization pass, but it is not in a state where repository metadata, CI, docs, and runtime surfaces all agree with each other. The fastest path to improvement is not another feature wave. It is consolidation, cleanup, and restoring trust in the build, docs, and app boundaries.
