# Enhancement Plan

Date: 2026-04-11
Repository: `Ethic-Latex`

## Goal

Turn the repository from a broad research monorepo with conflicting surfaces into a stable, reviewable project with one clear core, one clear application path, and reproducible developer workflows.

## Guiding Principles

- Prefer consolidation over adding another parallel surface.
- Keep `erh_core` as the real source of domain logic.
- Treat generated artifacts as outputs, not repository source.
- Make CI prove the same workflows that users and maintainers actually run.

## Phase 0: Decision Pass

Target: 1-2 days

- Decide the official backend surface.
- Decide the official frontend surface.
- Decide whether the security app is a first-class product or an experimental subproject.
- Decide whether `simulation/api/main.py` and `simulation/app.py` stay, move to `examples/`, or get archived.

Success criteria:

- One written architecture note naming the supported user-facing surfaces.
- One owner per supported surface.

## Phase 1: Stop the Known Breakages

Target: 2-4 days

- Fix `verify_rule_by_id` so it passes a `VerifyRequest` object or extracts shared verification logic into a helper.
- Refactor simulation background jobs to create their own SQLAlchemy session inside the task instead of reusing the request dependency session.
- Add the missing `HealthMonitorResponse` type and `getHealth()` client function in the Next.js security frontend, or remove the feature until the backend contract is complete.
- Add a smoke test for `POST /api/v1/verify/rule/{id}`.
- Add a smoke test that creates a simulation and verifies status transitions without leaking session state.
- Fix `simulation/app.py` by importing `json` and checking the results browser path end-to-end.

Success criteria:

- Security backend verification routes work from both direct-content and rule-id flows.
- Simulation jobs can run asynchronously without session errors.
- Security frontend builds cleanly.

Progress update (2026-04-12):

- The planned Phase 1 code fixes have been landed for the security backend/frontend surfaces.
- Added backend regression coverage for config defaults, `POST /api/v1/verify/rule/{id}`, simulation background-task session ownership, and the simulation create/status/results route flow.
- Verified on 2026-04-12 with `11` passing security backend tests plus successful Next.js frontend build and lint.
- The security frontend now also supports an explicit `typecheck` CI step, which starts landing the Phase 5 CI-signal cleanup for that surface.
- Root dependency and workflow support files were aligned so the repo-level environment can execute the backend router tests.
- The backend SQLite test harness now uses a process-specific temp database path so local parallel verification does not produce false collisions.
- `README.md` and `docs/IMPLEMENTATION_STATUS.md` now include a dated verified-surfaces snapshot and architecture map that reflects the latest repository-grounded evidence.
- `erh-security-app/README.md`, `docs/QUICKSTART.md`, and `docs/INSTALL.md` now distinguish the verified security app workflow from the broader research/simulation workflow.
- Remaining work after this tranche belongs primarily to the Phase 5/Phase 6 follow-up areas rather than the original known-breakage list.

## Phase 2: Rationalize Repo Boundaries

Target: 3-5 days

- Keep `erh_core` as canonical implementation code.
- Convert `erh/` and `simulation/core/` into thin, documented compatibility layers only.
- Archive or delete unused parallel frontends.
- Archive or delete unused parallel security frontend implementations if both Next.js and Vite are not needed.
- Rename or repackage `erh-security-app` if Python-level importability matters. A hyphenated directory is fine for deployment, but not ideal for package semantics.

Success criteria:

- A newcomer can identify the primary app and primary library in under five minutes.
- No duplicate user-facing surface remains without an explicit reason.

## Phase 3: Clean the Repository

Target: 2-3 days

- Remove tracked virtualenv contents.
- Remove tracked `node_modules`.
- Remove tracked built docs under `docs/_build`.
- Remove tracked notebook output logs and generated reports unless they are intentional fixtures.
- Remove editor-specific directories from Git unless they are explicitly part of the project contract.
- Replace checked-in generated outputs with `.gitkeep` where structure matters.
- Tighten `.gitignore` after the tracked files are removed.

Success criteria:

- Repository no longer tracks local environments or vendored dependencies.
- Clone and review size drops materially.
- `git status` noise from generated files is minimal after normal workflows.

## Phase 4: Rebuild Dependency Management

Target: 2-4 days

- Split Python dependency concerns into at least:
- core runtime
- dev/test
- docs/notebooks
- optional quantum or ML extras
- Make the root environment sufficient for the root test suite.
- Keep backend-only dependencies in the backend if it remains a separate deployable unit.
- Standardize one supported Python version range for active development.
- Standardize one supported Node version for active frontend work.

Success criteria:

- A fresh setup path is documented and reproducible.
- Backend tests do not fail due to missing baseline dependencies in the expected environment.

## Phase 5: Repair CI Signal

Target: 2-3 days

- Remove `continue-on-error` from checks that are supposed to be quality gates.
- Stop running commands that the package does not define.
- Add explicit frontend typecheck and build steps.
- Run backend tests in the same dependency model that maintainers are expected to use.
- Add a small smoke matrix:
- Python SDK tests
- security backend tests
- selected frontend build
- docs build if docs remain first-class

Success criteria:

- Red CI means something actionable broke.
- Green CI means the supported surfaces actually work.

## Phase 6: Repair Documentation

Target: 2-4 days

- Rewrite `README.md` around the chosen official surfaces.
- Update `docs/IMPLEMENTATION_STATUS.md` to match real file locations and current status.
- Remove claims that "all tests pass" unless they are backed by current CI evidence.
- Separate research notes from operational docs.
- Add a short architecture map with:
- canonical packages
- supported apps
- experimental areas
- archived or legacy compatibility layers

Success criteria:

- Documentation matches the repository that exists today.
- File paths referenced by docs exist.
- Status claims are tied to current verification evidence.

## Phase 7: Product Hardening

Target: ongoing after stabilization

- Add authorization to the security app instead of the current hard-coded user assumptions.
- Tighten CORS from wildcard defaults to environment-driven allowlists.
- Replace placeholder verification logic with a clearer contract to `erh_core`.
- Add schema and API contract tests for the security app.
- Add performance bounds for simulation endpoints and long-running jobs.

Success criteria:

- The supported app can be discussed as a product, not only as a prototype.

## Suggested Execution Order

1. Phase 0
2. Phase 1
3. Phase 5 for the changed surfaces
4. Phase 2
5. Phase 3
6. Phase 4
7. Phase 6
8. Phase 7

## First Week Deliverable

If only one week is available, the highest-value bundle is:

- fix the broken verification route
- fix the background session lifecycle
- make one frontend compile
- remove tracked virtualenv and `node_modules`
- update README and implementation status docs
- make CI enforce those exact paths

## Expected Outcome

After the plan, the repository should be smaller, easier to reason about, more reproducible to set up, and far more honest about what is supported versus experimental. That will increase development speed more than another feature drop would.
