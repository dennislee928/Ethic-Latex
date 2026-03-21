# ERH Hybrid Demo Design

**Date:** 2026-03-21

## Goal

Build a frontend that demonstrates the full Ethic-Latex project as both a research artifact and a live application. The app should use the root PDFs and generated figures as first-class content while also exposing live backend-powered analysis, simulation, ingestion, and LaTeX verification workflows.

## Product Direction

The approved direction is a hybrid landing experience rather than a research-only site or an operations-only dashboard. The home route should show the theory and the live system side by side. Users should be able to understand the ERH idea from the papers and figures, then immediately interact with the live API without leaving the page.

## User Experience

The main application remains the existing Vite React app in `frontend/`, but its information architecture becomes project-centric instead of security-placeholder-centric.

Primary routes:

- `/`: Hybrid home. Research overview, PDF shelf, figure gallery, judge selector, live analysis summary, ERH curves, health monitor, quick simulation launcher, and quick LaTeX verifier.
- `/dashboard`: Detailed live analysis and ingestion workspace. Includes summary, curves, heatmap, health monitor, code complexity tool, and ingestion controls.
- `/simulation`: Full simulation lab with run history, results, figure access, and richer narrative around the experiment outputs.
- `/editor`: LaTeX rule editor and verifier, aligned to the actual backend rule and verification endpoints.
- `/settings`: User preferences and API configuration.

## Research Asset Handling

The root PDFs are part of the product, not an afterthought. The app should surface:

- `ethical_riemann_hypothesis.pdf`
- `ethical_riemann_hypothesis_en.pdf`
- `ethical_riemann_hypothesis_zh.pdf`
- `ethical_riemann_hypothesis_en copy.pdf` only if kept intentionally visible

The generated figure PDFs in `figures/` and `simulation/output/figures/` should drive the visual storytelling. Instead of hardcoding fragile relative paths in the frontend, the backend should expose a small asset API that returns document and figure metadata plus stable download/view URLs.

## Backend Role

The FastAPI app in `erh-security-app/backend/` should remain the single runtime backend for the demo app. Existing live endpoints already cover most of the interactive surface:

- `/analysis/*`
- `/ingestion/*`
- `/api/v1/simulations/*`
- `/api/v1/rules/*`
- `/api/v1/verify/*`
- `/api/v1/settings/*`

New backend work is limited to asset discovery and reliable file serving. That includes:

- listing root PDFs and figure files
- exposing stable URLs for those assets
- fixing simulation figure URL serving so returned URLs match actual router prefixes and are fetchable

## Frontend Data Model

The frontend should use React Query for all remote state and a small shared store for view state such as:

- selected judge type
- selected document
- selected figure
- selected simulation
- active quick-action panel

Route components should not duplicate transformation logic. Shared API adapters and UI-friendly selectors should normalize backend responses once, especially for curves, heatmap cells, document metadata, and figure records.

## Failure Modes

The product must degrade gracefully. Likely missing or optional runtime conditions include:

- no analysis data yet
- no ingestion data loaded
- GitLab ingestion not configured
- HuggingFace or AITA loaders unavailable
- missing files in root or figure directories

In those cases, the UI should show a guided empty state with explicit next actions, not generic errors. The most important example is analysis: if no samples exist, users should get a one-click prompt to run mock ingestion.

## Visual Direction

The current frontend uses a generic dashboard shell. The redesign should adopt a stronger research-lab identity: paper-like structure, warm archival tones, precise typography, and charts/cards that feel like a computational notebook rather than a standard SaaS admin panel. It still needs to be responsive and fast, but it should visually communicate that the project mixes mathematics, simulation, and interactive tooling.

## Verification Strategy

Success requires evidence in three areas:

- backend tests for any new asset and simulation-file endpoints
- frontend tests for data normalization and critical empty/error states
- fresh build and test runs for both backend and frontend before claiming completion

This design is the validated basis for the implementation plan in `docs/plans/2026-03-21-erh-hybrid-demo.md`.
