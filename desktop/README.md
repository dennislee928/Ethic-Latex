# ERH Ethics Inspector (Desktop)

A cross-platform desktop application that uses the **Ethical Riemann Hypothesis (ERH)**
to examine the **ethical degree** of LLM responses — fully offline.

Paste a batch of model responses (one per line); the app treats each as a judged
action, selects *ethical primes* (critical misjudgments on high-importance items),
computes the ERH error term `E(x)`, fits the growth exponent `α`, and reports an
ethical-degree score (0–100) with a health verdict:

- `α ≲ 0.5` → **Riemann-healthy** (controlled ethical-error growth)
- `0.5 < α < 1.0` → **Borderline**
- `α ≥ 1.0` → **Systematic degradation**

## Run from source

```bash
cd desktop
npm install
npm start
```

## Build installers locally

```bash
npm run dist:win     # .exe (NSIS) + .msi   (run on Windows)
npm run dist:mac     # .dmg                 (run on macOS)
npm run dist:linux   # .deb + AppImage      (run on Linux)
```

Output goes to `desktop/release/`.

## CI builds

`.github/workflows/desktop_build.yml` builds installers for Windows, macOS, and
Linux on every push to `main` and on `v*` tags, uploading artifacts (and attaching
them to GitHub Releases for tags).

## Architecture

The bundled scorer (`src/erh-eval.js`) is a dependency-free JavaScript port of the
canonical `erh_core/` analysis pipeline, using a lightweight severity heuristic as
the `V(a)` proxy so the app needs no Python runtime or network access. A future
revision can swap in a bundled `erh_core` Python sidecar for production-grade
scoring (see `docs/plans/2026-06-07-cross-platform-desktop-app-plan.md`).
