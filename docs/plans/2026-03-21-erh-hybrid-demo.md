# ERH Hybrid Demo Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a hybrid ERH frontend that uses the root PDFs and generated figures as first-class research assets while exposing live backend-powered analysis, simulation, ingestion, and LaTeX verification features.

**Architecture:** Keep `frontend/` as the main React app and `erh-security-app/backend/` as the runtime backend. Add a small backend asset API plus simulation file-serving fixes, then refactor the frontend into a coherent ERH demo with a hybrid landing page and backend-aligned data model.

**Tech Stack:** FastAPI, SQLAlchemy, pytest, React, TypeScript, Vite, React Query, Zustand, Recharts, Vitest, Testing Library

---

### Task 1: Add Frontend Test Harness

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/tsconfig.app.json`
- Modify: `frontend/vite.config.ts`
- Create: `frontend/src/test/setup.ts`
- Create: `frontend/src/test/render.tsx`
- Create: `frontend/src/lib/__tests__/constants.test.ts`

**Step 1: Write the failing test**

Create `frontend/src/lib/__tests__/constants.test.ts` with a minimal route/config expectation, for example:

```ts
import { describe, expect, it } from 'vitest'
import { ROUTES } from '@/lib/constants'

describe('ROUTES', () => {
  it('defines the hybrid home route at slash', () => {
    expect(ROUTES.HOME).toBe('/')
  })
})
```

**Step 2: Run test to verify it fails**

Run: `npm test -- --run frontend/src/lib/__tests__/constants.test.ts`

Expected: FAIL because no test runner or `ROUTES.HOME` exists yet.

**Step 3: Write minimal implementation**

- Add `vitest`, `jsdom`, `@testing-library/react`, and `@testing-library/jest-dom` to `frontend/package.json`
- Add a `test` script
- Add Vitest config to `frontend/vite.config.ts`
- Add `ROUTES.HOME`

**Step 4: Run test to verify it passes**

Run: `npm test -- --run frontend/src/lib/__tests__/constants.test.ts`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/package.json frontend/tsconfig.app.json frontend/vite.config.ts frontend/src/test/setup.ts frontend/src/test/render.tsx frontend/src/lib/__tests__/constants.test.ts frontend/src/lib/constants.ts
git commit -m "test: add frontend test harness"
```

### Task 2: Add Backend Asset Listing Endpoint

**Files:**
- Modify: `erh-security-app/backend/app/main.py`
- Create: `erh-security-app/backend/app/routers/assets.py`
- Create: `erh-security-app/backend/tests/test_assets_router.py`

**Step 1: Write the failing test**

Create a backend test that requests the new asset index and asserts that root papers and figure collections are included.

```python
def test_assets_index_lists_root_pdfs_and_figures(client):
    response = client.get("/assets/index")

    assert response.status_code == 200
    payload = response.json()
    assert any(doc["name"] == "ethical_riemann_hypothesis.pdf" for doc in payload["documents"])
    assert "figures" in payload
```

**Step 2: Run test to verify it fails**

Run: `pytest erh-security-app/backend/tests/test_assets_router.py -q`

Expected: FAIL with 404 or import errors because the router does not exist.

**Step 3: Write minimal implementation**

- Add `assets.py` router
- Index root-level PDFs
- Index `figures/*.pdf` and `simulation/output/figures/*.pdf`
- Return stable metadata including `name`, `category`, `relative_path`, and `url`
- Register router in `app/main.py`

**Step 4: Run test to verify it passes**

Run: `pytest erh-security-app/backend/tests/test_assets_router.py -q`

Expected: PASS

**Step 5: Commit**

```bash
git add erh-security-app/backend/app/main.py erh-security-app/backend/app/routers/assets.py erh-security-app/backend/tests/test_assets_router.py
git commit -m "feat: add backend asset index"
```

### Task 3: Fix Simulation Figure Serving

**Files:**
- Modify: `erh-security-app/backend/app/routers/simulate.py`
- Create: `erh-security-app/backend/tests/test_simulate_router_assets.py`

**Step 1: Write the failing test**

Add a test that verifies figure URLs returned by `/api/v1/simulations/{id}/figures` are fetchable and use the correct prefix.

```python
def test_simulation_figures_use_fetchable_urls(client, completed_simulation):
    response = client.get(f"/api/v1/simulations/{completed_simulation.id}/figures")

    assert response.status_code == 200
    figure = response.json()["figures"][0]
    assert figure["path"].startswith(f"/api/v1/simulations/{completed_simulation.id}/figures/")
```

**Step 2: Run test to verify it fails**

Run: `pytest erh-security-app/backend/tests/test_simulate_router_assets.py -q`

Expected: FAIL because returned paths do not match a real serving route.

**Step 3: Write minimal implementation**

- Fix the path prefix to match `/api/v1/simulations`
- Add a file-serving route for individual figure assets using `FileResponse`
- Ensure nonexistent files return 404

**Step 4: Run test to verify it passes**

Run: `pytest erh-security-app/backend/tests/test_simulate_router_assets.py -q`

Expected: PASS

**Step 5: Commit**

```bash
git add erh-security-app/backend/app/routers/simulate.py erh-security-app/backend/tests/test_simulate_router_assets.py
git commit -m "fix: serve simulation figure assets"
```

### Task 4: Align Frontend API Types To Backend Contracts

**Files:**
- Modify: `frontend/src/api/dashboard.ts`
- Modify: `frontend/src/api/simulate.ts`
- Modify: `frontend/src/api/rules.ts`
- Modify: `frontend/src/api/verify.ts`
- Create: `frontend/src/api/assets.ts`
- Create: `frontend/src/types/assets.ts`
- Create: `frontend/src/lib/__tests__/asset-normalizers.test.ts`

**Step 1: Write the failing test**

Write a small normalization test for backend asset payloads.

```ts
import { describe, expect, it } from 'vitest'
import { toAssetGroup } from '@/api/assets'

describe('toAssetGroup', () => {
  it('normalizes document and figure urls', () => {
    const payload = { documents: [{ name: 'paper.pdf', url: '/assets/files/paper.pdf' }], figures: [] }
    expect(toAssetGroup(payload).documents[0].url).toBe('/assets/files/paper.pdf')
  })
})
```

**Step 2: Run test to verify it fails**

Run: `npm test -- --run frontend/src/lib/__tests__/asset-normalizers.test.ts`

Expected: FAIL because the adapter does not exist.

**Step 3: Write minimal implementation**

- Add asset types and API client
- Remove placeholder dashboard stats or replace them with derived live stats
- Keep endpoint paths exactly aligned with backend router prefixes

**Step 4: Run test to verify it passes**

Run: `npm test -- --run frontend/src/lib/__tests__/asset-normalizers.test.ts`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/api/dashboard.ts frontend/src/api/simulate.ts frontend/src/api/rules.ts frontend/src/api/verify.ts frontend/src/api/assets.ts frontend/src/types/assets.ts frontend/src/lib/__tests__/asset-normalizers.test.ts
git commit -m "refactor: align frontend api contracts"
```

### Task 5: Build Shared ERH Demo State And Layout

**Files:**
- Modify: `frontend/src/lib/constants.ts`
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/components/layout/Layout.tsx`
- Modify: `frontend/src/components/layout/Sidebar.tsx`
- Modify: `frontend/src/components/layout/Header.tsx`
- Create: `frontend/src/store/demoStore.ts`
- Create: `frontend/src/components/layout/JudgePicker.tsx`
- Create: `frontend/src/components/layout/PageIntro.tsx`
- Create: `frontend/src/components/layout/EmptyState.tsx`
- Test: `frontend/src/components/layout/__tests__/judge-picker.test.tsx`

**Step 1: Write the failing test**

Add a render test that confirms the judge picker updates the shared selected judge type.

```tsx
it('updates the selected judge type', async () => {
  render(<JudgePicker />)
  await userEvent.click(screen.getByRole('button', { name: /human/i }))
  expect(useDemoStore.getState().judgeType).toBe('HUMAN')
})
```

**Step 2: Run test to verify it fails**

Run: `npm test -- --run frontend/src/components/layout/__tests__/judge-picker.test.tsx`

Expected: FAIL because the store and component do not exist.

**Step 3: Write minimal implementation**

- Introduce `ROUTES.HOME`
- Add the shared demo store
- Replace the generic product framing in sidebar/header
- Add a stronger visual system in `index.css`

**Step 4: Run test to verify it passes**

Run: `npm test -- --run frontend/src/components/layout/__tests__/judge-picker.test.tsx`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/lib/constants.ts frontend/src/index.css frontend/src/components/layout/Layout.tsx frontend/src/components/layout/Sidebar.tsx frontend/src/components/layout/Header.tsx frontend/src/store/demoStore.ts frontend/src/components/layout/JudgePicker.tsx frontend/src/components/layout/PageIntro.tsx frontend/src/components/layout/EmptyState.tsx frontend/src/components/layout/__tests__/judge-picker.test.tsx
git commit -m "feat: add shared erh demo layout"
```

### Task 6: Build The Hybrid Home Route

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/pages/Dashboard.tsx`
- Create: `frontend/src/components/home/HeroPanel.tsx`
- Create: `frontend/src/components/home/DocumentShelf.tsx`
- Create: `frontend/src/components/home/FigureGallery.tsx`
- Create: `frontend/src/components/home/AnalysisOverview.tsx`
- Create: `frontend/src/components/home/QuickSimulation.tsx`
- Create: `frontend/src/components/home/QuickVerifier.tsx`
- Test: `frontend/src/pages/__tests__/dashboard-home.test.tsx`

**Step 1: Write the failing test**

Add a page-level test that verifies the home route renders both research and live sections.

```tsx
it('renders research assets and live lab panels together', async () => {
  render(<Dashboard />)
  expect(screen.getByText(/research papers/i)).toBeInTheDocument()
  expect(screen.getByText(/live analysis/i)).toBeInTheDocument()
})
```

**Step 2: Run test to verify it fails**

Run: `npm test -- --run frontend/src/pages/__tests__/dashboard-home.test.tsx`

Expected: FAIL because the new home composition does not exist.

**Step 3: Write minimal implementation**

- Compose the new hybrid landing page
- Fetch assets, summary, curves, and health state
- Add robust empty/error states when analysis data is unavailable
- Add quick actions for mock ingestion, simulation, and verification

**Step 4: Run test to verify it passes**

Run: `npm test -- --run frontend/src/pages/__tests__/dashboard-home.test.tsx`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/App.tsx frontend/src/pages/Dashboard.tsx frontend/src/components/home/HeroPanel.tsx frontend/src/components/home/DocumentShelf.tsx frontend/src/components/home/FigureGallery.tsx frontend/src/components/home/AnalysisOverview.tsx frontend/src/components/home/QuickSimulation.tsx frontend/src/components/home/QuickVerifier.tsx frontend/src/pages/__tests__/dashboard-home.test.tsx
git commit -m "feat: build hybrid home route"
```

### Task 7: Refactor The Analysis Workspace

**Files:**
- Modify: `frontend/src/pages/Simulation.tsx`
- Modify: `frontend/src/pages/Editor.tsx`
- Modify: `frontend/src/pages/Settings.tsx`
- Modify: `frontend/src/components/simulation/FigureViewer.tsx`
- Modify: `frontend/src/components/dashboard/ActivityFeed.tsx`
- Modify: `frontend/src/components/dashboard/LinterStats.tsx`
- Modify: `frontend/src/components/dashboard/RiskHeatmap.tsx`
- Modify: `frontend/src/components/dashboard/SecurityMetrics.tsx`
- Create: `frontend/src/components/dashboard/IngestionControls.tsx`
- Create: `frontend/src/components/dashboard/HealthMonitor.tsx`
- Create: `frontend/src/components/dashboard/ComplexityTool.tsx`

**Step 1: Write the failing test**

Add one route-level test asserting the dashboard workspace can show ingestion controls and health monitor when there is no data.

```tsx
it('shows guided ingestion controls when no analysis data exists', async () => {
  render(<AnalysisWorkspace />)
  expect(screen.getByText(/run mock ingestion/i)).toBeInTheDocument()
})
```

**Step 2: Run test to verify it fails**

Run: `npm test -- --run frontend/src/components/dashboard/__tests__/analysis-workspace.test.tsx`

Expected: FAIL because the workspace composition does not exist.

**Step 3: Write minimal implementation**

- Replace placeholder security metrics with ERH-specific summaries
- Add ingestion controls for mock, GitLab, HuggingFace, and AITA modes where applicable
- Add complexity analysis input wired to `/analysis/complexity`
- Update simulation and editor pages to match the new demo language and backend behavior

**Step 4: Run test to verify it passes**

Run: `npm test -- --run frontend/src/components/dashboard/__tests__/analysis-workspace.test.tsx`

Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/pages/Simulation.tsx frontend/src/pages/Editor.tsx frontend/src/pages/Settings.tsx frontend/src/components/simulation/FigureViewer.tsx frontend/src/components/dashboard/ActivityFeed.tsx frontend/src/components/dashboard/LinterStats.tsx frontend/src/components/dashboard/RiskHeatmap.tsx frontend/src/components/dashboard/SecurityMetrics.tsx frontend/src/components/dashboard/IngestionControls.tsx frontend/src/components/dashboard/HealthMonitor.tsx frontend/src/components/dashboard/ComplexityTool.tsx
git commit -m "feat: refactor analysis and lab workspaces"
```

### Task 8: Verify End-To-End

**Files:**
- Modify: `frontend/README.md`
- Modify: `README.md`

**Step 1: Run backend targeted tests**

Run: `pytest erh-security-app/backend/tests/test_assets_router.py erh-security-app/backend/tests/test_simulate_router_assets.py erh-security-app/backend/tests/test_analysis_router.py -q`

Expected: PASS

**Step 2: Run frontend targeted tests**

Run: `npm test -- --run`

Expected: PASS

**Step 3: Run frontend build**

Run: `npm run build`

Expected: PASS

**Step 4: Update docs**

- Document the hybrid demo routes and backend asset requirements
- Update local development instructions if new frontend test tooling is added

**Step 5: Commit**

```bash
git add frontend/README.md README.md
git commit -m "docs: document hybrid erh demo"
```

## Notes

- Do not remove existing user changes outside the touched files.
- Prefer deriving “stats” from real backend responses instead of carrying placeholder dashboard numbers.
- If backend data is absent, the UI must guide the user toward mock ingestion instead of showing blank charts.
- Keep the route structure stable so existing links to `/`, `/editor`, `/simulation`, and `/settings` keep working.

Plan complete and saved to `docs/plans/2026-03-21-erh-hybrid-demo.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
