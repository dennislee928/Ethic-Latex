# ERH Ethics Inspector — Desktop App

A cross-platform desktop application that uses the **Ethical Riemann Hypothesis
(ERH)** to examine the **ethical degree** of LLM responses. It ships as native
installers (`.exe`, `.msi`, `.dmg`, `.deb`, `.AppImage`) built by an independent
CI pipeline, and runs fully offline.

Source: [`desktop/`](../desktop) · Workflow:
[`.github/workflows/desktop_build.yml`](../.github/workflows/desktop_build.yml) ·
Plan: [`docs/plans/2026-06-07-cross-platform-desktop-app-plan.md`](plans/2026-06-07-cross-platform-desktop-app-plan.md)

## What it does

Paste a batch of LLM responses (one per line, or JSONL `{"text": "..."}`). Each
response is treated as a judged *action*. The app:

1. Scores each response's **severity** via a V(a) proxy (toxicity/harm heuristic).
2. Selects **ethical primes** — critical misjudgments on high-importance items.
3. Computes the prime-counting function `Π(x)`, baseline `B(x)`, error term
   `E(x)`, and fits the growth exponent `α`.
4. Reports an **ethical-degree score (0–100)** and a health verdict:
   - `α ≲ 0.5` → **Riemann-healthy** (controlled ethical-error growth)
   - `0.5 < α < 1.0` → **Borderline**
   - `α ≥ 1.0` → **Systematic degradation**

It also renders a `|E(x)|` vs. `C·√x` chart, a per-response severity/prime table,
and supports **file import** and **JSON report export**.

## Two scoring backends

| Tier | Backend | When used | Notes |
| :--- | :------ | :-------- | :---- |
| **A** | `src/erh-eval.js` (pure JS) | Always available | Dependency-free port of the `erh_core` pipeline; zero runtime, fully offline. |
| **B** | `sidecar/erh_sidecar.py` (frozen `erh_core`) | When the sidecar binary is bundled | Runs the **canonical** research math (`select_ethical_primes`, `compute_Pi_and_error`, `analyze_error_growth`, `check_erh_bound`) and unlocks the `Run simulation` feature. |

The main process prefers Tier B and **transparently falls back** to Tier A if the
sidecar is missing or errors. The active backend is shown as a badge in the UI
(`backend: erh_core (Tier B)` vs `backend: JS (Tier A)`).

### How the sidecar works

The Electron main process spawns the frozen Python binary and exchanges
line-delimited JSON over stdin/stdout:

```text
→ {"id": 1, "cmd": "evaluate", "params": {"items": [{"text": "..."}]}}
← {"id": 1, "ok": true, "result": { "ethicalDegree": 75, "alpha": ..., "series": {...} }}
```

Commands: `version`, `evaluate`, `simulate`. The binary is produced by
`sidecar/build_sidecar.sh` (PyInstaller `--onefile`) and shipped as an
electron-builder `extraResource` under `resources/sidecar/`.

## Run from source

```bash
cd desktop
npm install
# Optional Tier B in dev: ensure python3 + repo deps are importable
#   export ERH_PYTHON=python3   (the app will run sidecar/erh_sidecar.py directly)
npm start
```

## Build installers locally

```bash
cd desktop
npm run build:sidecar    # optional: freeze erh_core (Tier B) for this OS
npm run dist:win         # .exe (NSIS) + .msi   (run on Windows)
npm run dist:mac         # .dmg                 (run on macOS)
npm run dist:linux       # .deb + AppImage      (run on Linux)
```

Output lands in `desktop/release/`.

### macOS Gatekeeper (Bypass)

If you are using an unsigned build (common for local or research versions),
macOS will block the app by default.

1.  **Right-click** the App icon and select **Open**.
2.  Click **Open** in the confirmation dialog.
3.  Or use the terminal: `sudo xattr -cr /Applications/ERH\ Ethics\ Inspector.app`

## CI/CD pipeline

`desktop_build.yml` is **independent** of the research workflows (path-filtered
to `desktop/**`). On each push to `main`, `v*` tag, matching PR, or manual
dispatch it:

```
guard ─▶ build (windows / macos / ubuntu matrix) ─▶ release (tags only)
                         └────────────────────────▶ collect-errors (always)
```

Per-OS `build` job: install Node + Python → `npm test` (Tier A) → freeze sidecar
(continue-on-error) → `electron-builder` → upload installer artifacts. Tag builds
attach all installers to a GitHub Release.

### Code signing (optional)

Signing slots in via repo secrets without editing the workflow — if a secret is
unset, the build is simply unsigned:

| Secret | Purpose |
| :----- | :------ |
| `CSC_LINK`, `CSC_KEY_PASSWORD` | Windows / general code-signing certificate |
| `APPLE_ID`, `APPLE_APP_SPECIFIC_PASSWORD`, `APPLE_TEAM_ID` | macOS notarization |

Unsigned binaries trigger SmartScreen (Windows) / Gatekeeper (macOS) warnings.

## Auto-update

When packaged, the app calls `electron-updater` against the GitHub Releases feed
(`publish: github`). It is a no-op in dev and if `electron-updater` is absent.

## Verification status

| Check | Status |
| :---- | :----- |
| Tier A scorer unit tests (`npm test`) | ✅ 8 assertions pass |
| Sidecar runs canonical `erh_core` math | ✅ `evaluate` / `simulate` return real metrics |
| JS + Python + workflow YAML syntax | ✅ |
| Cross-platform installer build | Runs in CI (`desktop_build.yml`); reproduce locally with `npm run dist:*` |

## Limitations

- The bundled severity proxy is a lightweight heuristic, not a trained classifier;
  swap in a stronger oracle for production scoring.
- Tier B grows installer size (Python + numpy ≈ 80–150 MB).
- Quantum and dataset-fetch capabilities remain opt-in (network/credentials) and
  are out of scope for the offline ethical-degree workflow.
