# ERH Ethics Inspector (Desktop)

A cross-platform desktop application that uses the **Ethical Riemann Hypothesis
(ERH)** to examine the **ethical degree** of LLM responses — fully offline.

Paste a batch of model responses (one per line, or JSONL `{"text": "..."}`); the
app treats each as a judged action, selects *ethical primes* (critical
misjudgments on high-importance items), computes the ERH error term `E(x)`, fits
the growth exponent `α`, and reports an ethical-degree score (0–100) with a
health verdict:

- `α ≲ 0.5` → **Riemann-healthy** (controlled ethical-error growth)
- `0.5 < α < 1.0` → **Borderline**
- `α ≥ 1.0` → **Systematic degradation**

Features: file import, JSON report export, per-response severity/prime table, and
an inline `|E(x)|` vs `C·√x` chart.

**Full documentation:** [`../docs/DESKTOP_APP.md`](../docs/DESKTOP_APP.md).

## Two scoring backends

- **Tier A — JS scorer** (`src/erh-eval.js`): dependency-free port of the
  `erh_core` pipeline. Always available, zero runtime.
- **Tier B — `erh_core` sidecar** (`sidecar/erh_sidecar.py`): the canonical
  research math, frozen with PyInstaller and bundled as an `extraResource`. The
  app prefers it and falls back to Tier A automatically. Also enables the
  `Run simulation` button.

## Run from source

```bash
cd desktop
npm install
npm start            # set ERH_PYTHON=python3 to enable the Tier B sidecar in dev
```

## Test

```bash
npm test             # Tier A scorer assertions
```

## Build installers locally

```bash
npm run build:sidecar   # optional: freeze erh_core (Tier B) for this OS
npm run dist:win        # .exe (NSIS) + .msi   (run on Windows)
npm run dist:mac        # .dmg                 (run on macOS)
npm run dist:linux      # .deb + AppImage      (run on Linux)
```

Output goes to `desktop/release/`.

## macOS Gatekeeper (Bypass)

Since this is an academic/research project, local builds and GitHub artifacts
may be **unsigned**. When you open the `.dmg` or `.app` on macOS, you might see
a warning that the developer cannot be verified.

**To bypass this:**
1.  **Right-click** (or Control-click) the App icon and select **Open**.
2.  In the dialog that appears, click **Open** again.
3.  Alternatively, if the app still won't run, execute this in your terminal:
    ```bash
    sudo xattr -cr /Applications/ERH\ Ethics\ Inspector.app
    ```

## CI builds

`.github/workflows/desktop_build.yml` builds installers for Windows, macOS, and
Linux on every push to `main` and on `v*` tags, runs the Tier A tests, freezes
the sidecar, uploads artifacts, and attaches them to GitHub Releases for tags.
Code signing slots in via repo secrets (`CSC_LINK`, `APPLE_ID`, …).

## Layout

```text
desktop/
├── src/
│   ├── main.js          # Electron main: IPC, sidecar+fallback, files, auto-update
│   ├── preload.js       # contextBridge API
│   ├── sidecar.js       # spawns/drives the erh_core sidecar
│   ├── erh-eval.js      # Tier A pure-JS scorer
│   └── renderer/        # UI (index.html, renderer.js)
├── sidecar/
│   ├── erh_sidecar.py   # Tier B: canonical erh_core over JSON/stdio
│   └── build_sidecar.sh # PyInstaller freeze
├── test/erh-eval.test.js
├── build/               # icons (icon.png, icon.ico)
└── package.json         # electron-builder config (win/mac/linux targets)
```
