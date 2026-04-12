# Supported Surfaces

Status date: `2026-04-12`

This note records the repository's currently supported user-facing surfaces and the boundary between supported, compatibility, and experimental areas. It is the project-level decision record referenced by the enhancement plan's Phase 0 and Phase 2 work.

## Decision Summary

- **Official backend surface:** `erh-security-app/backend`
- **Official frontend surface:** `erh-security-app/frontend`
- **Canonical implementation library:** `erh_core/`
- **Security app status:** first-class supported application surface for the current operational path
- **Research/simulation status:** supported as research and reproduction tooling, not as the primary operational app
- **Duplicate UI surfaces:** retained in-tree for now, but not part of the current supported app path

## Supported User-Facing Surfaces

### Security App Backend

- **Path:** `erh-security-app/backend`
- **Role:** FastAPI backend for the ERH-on-Security application
- **Current status:** supported and revalidated
- **Verification evidence:** backend regression suite passes with route coverage for verification and simulation flows
- **Provisional owner:** repository maintainer (`dennislee928`)

### Security App Frontend

- **Path:** `erh-security-app/frontend`
- **Role:** Next.js frontend for the ERH-on-Security application
- **Current status:** supported and revalidated
- **Verification evidence:** `typecheck`, `build`, and `lint` pass
- **Provisional owner:** repository maintainer (`dennislee928`)

### Research and Reproduction Surface

- **Paths:** `simulation/`, `erh/`, `erh_core/`, LaTeX paper sources, root tests
- **Role:** research code, paper reproduction, SDK-style access, and experiments
- **Current status:** supported for research and paper reproduction, but not the primary operational app surface
- **Verification evidence:** root SDK and ERH Phase 1 checks pass; reviewer and quickstart docs point here for paper reproduction
- **Provisional owner:** repository maintainer (`dennislee928`)

## Compatibility and Experimental Areas

### Compatibility Layers

- **Paths:** `erh/`, `simulation/core/`, selected `simulation/analysis/`
- **Intent:** preserve older import paths while keeping `erh_core/` as the real source of domain logic

### Experimental or Duplicate App/UI Surfaces

- **`frontend/`**
  Separate root frontend. Keep treated as experimental until revalidated or archived.
- **`erh-security-app/frontend-vite/`**
  Alternate security frontend implementation. Not part of the current supported app path.
- **`simulation/api/main.py`**
  Research/demo API surface. Not the official backend surface.
- **`simulation/app.py`**
  Research/demo Streamlit entrypoint. Keep as a utility path, not the official frontend surface.

## Decision Implications

- New operational fixes should target `erh-security-app/backend` and `erh-security-app/frontend` first.
- Shared domain logic should continue moving toward `erh_core/`.
- Documentation should present the security app as the primary application path and the simulation stack as the research path.
- Duplicate UI surfaces should either be archived or justified explicitly before being treated as supported.
