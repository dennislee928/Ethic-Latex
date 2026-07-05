# ERH Ethics Inspector — v2 Report (Desktop Hardening, i18n, Recommendation Rollout)

**Date:** 2026-07-05 · **Branch:** `feature/erh-engine` · **Release tag:** `v0.1.1`
**Commits:** `5f5221e` (desktop v2 + recommendations), `320d0c8` (0.1.1 bump), `8351d09` (npm idempotency)
**Supersedes:** [report.md](report.md) (v1 — scoring recalibration & rebuild)

---

## 1. What the new screenshots and exports showed

Six screenshots of the running v1-recalibrated app plus two Tier B exports
(`erh-report.deepseek.json`, `erh-report.deekseek.json`) were analyzed.

**Confirmed working from v1:** the recalibrated score is live — a DeepSeek batch
(N=48, α=0.5636) now reads **Borderline 74/100** instead of the old
"healthy 96"; the parameters panel, breakdown bars, and how-to-read section all
render.

**New defects found (all fixed):**

| # | Finding | Root cause | Fix |
|---|---|---|---|
| 1 | **Run Research Simulation crashed** with `float() argument must be a string or a real number, not 'NoneType'` (visible in screenshot 6) | `erh_core`'s `Action.severity` *defaults to `None`*, so `getattr(a, "severity", fallback)` returns None — the attribute always exists — and `float(None)` throws | Explicit None guard in the sidecar severity accessor |
| 2 | **Prime indicators "miss sometimes"** | Two causes: (a) Tier B results contained **no `items` at all** (both DeepSeek exports show `items: 0`), so the response table lost its flags whenever the sidecar answered; (b) responses above the severity threshold but below the importance quantile were labeled **"Safe"** | (a) The sidecar now returns per-item rows (text, severity, complexity, `isPrime`, `isMisjudged`); (b) tri-state status: **🚩 Prime / ⚠ Misjudged / Safe** |
| 3 | Verdict said *healthy* but rendered **amber** (score 71 < the 75 color line) | Color was keyed to the numeric score, not the tier | Verdict/badge/gauge now take the tier's color; component bars keep the numeric scale |

## 2. Desktop enhancements delivered

- **Traditional Chinese (繁體中文) UI** — a header **EN/繁中** toggle
  (persisted in `localStorage`) translates every static element: subtitle,
  banner, input labels, placeholder, all seven buttons, the parameters panel,
  metric labels/hints, table headers, status labels, chart legend + reading
  guide, verdict-tier explanations, and the full "how to read the results"
  section. Result cards re-render in the selected language.
- **Tri-state response table** (see above) so serious-but-not-prime responses
  are visibly ⚠ flagged.
- **Tier B per-item rows** — the table, flags, and severities now work
  identically on both backends.

## 3. All seven app functions tested

A new headless renderer harness (`desktop/test/renderer.test.js`) stubs the DOM
and preload bridge and drives the real handler code:

| Function | Verified behavior |
|---|---|
| Run Analysis | renders verdict card + breakdown; forwards severity/quantile/C parameters; tri-state status present |
| Format to JSONL | extracts messages from raw JSON/API streams and rewrites input as `{"text": ...}` lines |
| Reset | clears input/output, disables Export |
| Debug Log | exports raw input, parsed items, and backend info |
| Import File | fills the input area from the chosen file |
| Export Report | exports the last result object (with `ethicalDegree`) |
| Run Research Simulation | forwards quantile/C; renders the Tier B-shaped result |
| EN/繁中 toggle | static + re-rendered dynamic text switches both ways |

**Totals:** desktop 14 + 16 = **30 assertions**, Python **152 passed** (was
146; +lexicon parity, +over-refusal), engine parity 7/7, Go gateway
`build`+`vet` clean. The frozen sidecar was protocol-tested (simulate: 150
items, tier healthy; evaluate: items present) and the packaged app was
launched and verified to contain the zh-TW strings, tri-state labels, bundled
lexicon, and the new 291.4 MB sidecar.

## 4. v1 "Remaining recommendations" — all six implemented

1. **Tag `v0.1.1`** — desktop version bumped, annotated tag pushed; the tag
   pipeline builds all installers and publishes the GitHub Release **with
   `latest*.yml` + blockmaps**, activating auto-update end-to-end.
2. **Must-fail gate fixture** — `erh-llm-gate.yml` now asserts the compromised
   fixture *fails* at `--max-risk 25`; if it ever passes, the merge is blocked.
   Verified live in CI: *"Compromised fixture correctly failed the gate
   (sensitivity intact)."*
3. **Unified ethics lexicon** — canonical `shared/ethics_lexicon.json`
   consumed by the desktop JS scorer (bundled copy), the Python sidecar
   (file-first with embedded fallback), the engine adapter, and the Go gateway
   (`go:embed`); `tests/test_lexicon_parity.py` fails the build if any copy or
   embedded fallback drifts.
4. **Over-refusal axis** — `refusal_score()` in the engine: refusing a
   *benign* prompt now pulls J down (a detectable misjudgment), while refusing
   a harmful prompt stays correct behavior. Covered by three new tests.
5. **Session-window ERH at the gateway** — the Go gateway keeps a rolling
   32-exchange window per client (`X-Client-Id` header, else client IP) and
   evaluates the whole window, so the verdict reflects the session's
   error-growth trajectory (the actual ERH signal) instead of a degenerate
   single sample.
6. **Pluggable oracle** — `ERH_ORACLE_MODEL` env var selects the HF checkpoint
   (e.g. a policy/compliance classifier) without code changes.

## 5. Rebuild + CI/CD results (commit `5f5221e`)

### Local
`ERH Ethics Inspector-0.1.0-arm64.dmg` (385.6 MB) + `.zip` (381.1 MB) + both
blockmaps + `latest-mac.yml`, re-frozen sidecar inside, launch-verified.

### GitHub Actions

| Workflow | Result |
|---|---|
| Desktop App (Cross-Platform Installers) | ✅ Windows 320 MB · Linux 372 MB · macOS 287 MB |
| Build Thesis (Single Script) | ✅ EN 46 pp / ZH 37 pp, ~16 figures each, **0 unresolved references** |
| ERH Engine (incl. new over-refusal + parity tests) | ✅ |
| ERH LLM Gate (incl. new sensitivity must-fail) | ✅ |
| Repository Smoke | ✅ |
| `v0.1.1` tag: Desktop release / Python SDK / Julia | 🔄 running at time of writing (release publishes installers + updater feed on completion) |
| `v0.1.1` tag: Node.js SDK | ⚠ `npm publish` 404 — the `NPM_TOKEN` secret is invalid/expired (npm masks auth failures as 404) and `erh-js-sdk@0.1.1` already exists; publish step made idempotent (`8351d09`), **token must be rotated by the repo owner** |

### PDFs (pulled from the v2 CI run)

Both thesis PDFs rebuilt cleanly from the updated pipeline: EN 46 pages / ZH 37
pages, ~16 embedded figures each, zero unresolved `??` references — unchanged
from v1, confirming the desktop/scoring changes did not disturb the research
artifact chain.

## 6. What to do next

1. **Rotate `NPM_TOKEN`** (npm → Access Tokens → Automation) so tag publishes
   work; PyPI's `--skip-existing` already makes the Python side idempotent.
2. Once the `v0.1.1` release is live, install from the published DMG and
   confirm the in-app updater finds `latest-mac.yml` (the previous 404 becomes
   a "no update available" no-op).
3. Consider swapping `ERH_ORACLE_MODEL` to a policy/compliance classifier for
   the gate and comparing risk scores against toxic-bert on the two fixtures.
4. The gateway session windows live in memory; add TTL eviction before running
   it as a long-lived multi-tenant service.
5. zh-TW currently covers static UI; verdict strings from the backends are
   English — localize them next if the app targets zh-first users.

---

*Generated by Claude Code on 2026-07-05. Numbers reproduced from local runs and
CI artifacts on `feature/erh-engine` (`5f5221e`…`8351d09`) and the `v0.1.1` tag.*
