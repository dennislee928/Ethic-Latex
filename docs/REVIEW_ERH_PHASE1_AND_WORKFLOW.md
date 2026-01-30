# Review: ERH Phase 1 Implementation & build_thesis Workflow

**Review date:** 2025-01-30  
**Scope:** All changes for cursor.plan.md Phase 1 + `build_thesis.yml` LLM step.  
**Skills applied:** receiving-code-review, requesting-code-review, verification-before-completion, systematic-debugging.

---

## 1. Plan vs implementation checklist

| Plan item | Status | Location / note |
|-----------|--------|------------------|
| 1.1 Generate 10k scenarios (ETHICS-style) | Done | `erh/core/action_space.py` + `erh/core/scenario_generator.py` |
| 1.1 `scripts/llm_stress_test.py` + OpenAI/Anthropic | Done | `scripts/llm_stress_test.py` (requests, no extra deps) |
| 1.2 EthicalPrimalityTest at complexity x | Done | `erh/core/ethical_primes.py` → `ethical_primality_test()` |
| 1.3 Π(x), E(x) charts | Done | Script writes `llm_stress_test_Pi_E.png` when matplotlib present |
| 1.3 Compare α across models | Optional | Run script for multiple providers, aggregate `llm_stress_test_summary.json` |
| Workflow: API keys (OPENAI / ANTHROPIC) | Done | Secrets in `build_thesis.yml` |
| Workflow: Default small-scale (100 actions) | Done | With key: 100 actions; no key: dry-run |
| Workflow: Copy figure to LaTeX | Done | `Prepare Figures` copies `llm_stress_test_Pi_E.png` → `figures/` |
| Workflow: Upload LLM results | Done | Artifact `llm_stress_test_results`, 14 days |

---

## 2. Files changed (summary)

- **New:** `erh/core/scenario_generator.py` – ETHICS-style prompts, V not revealed.
- **New:** `scripts/llm_stress_test.py` – generate world, call API, Π/E, charts, dry-run.
- **New:** `tests/test_erh_phase1.py` – unit tests for scenario_generator and ethical_primality_test.
- **Modified:** `erh/core/ethical_primes.py` – added `ethical_primality_test()`; `np.where` → `np.flatnonzero`.
- **Modified:** `erh/core/__init__.py` – exports for scenario_generator and ethical_primality_test.
- **Modified:** `.github/workflows/build_thesis.yml` – LLM step, figure copy, artifact upload.
- **Modified:** `.cursor/plan/cursor.plan.md` – Phase 1 checkboxes and notes.
- **Removed:** Unused `evaluate_judgement` import in `llm_stress_test.py`.

---

## 3. Verification (evidence before claims)

**Verification-before-completion:** Run these locally and confirm output before relying on “done”.

**Option A – Single script (recommended if terminal is slow or you can’t run multiple commands):**

```bash
cd D:\GitHub\Ethic-Latex
python scripts/run_verification_phase1.py
```

This runs all three checks in one process (imports + ethical_primality_test, dry-run, pytest). Exit code 0 = all passed.

**Option B – Three separate commands:**

```bash
cd D:\GitHub\Ethic-Latex

# 1) Imports and ethical_primality_test
python -c "from erh.core import ethical_primality_test, actions_to_prompts; from erh.core.action_space import generate_world; w=generate_world(10,random_seed=42); p=actions_to_prompts(w); assert len(p)==10; import numpy as np; E=np.array([0.1,0.2,0.5,0.3,0.2]); x=np.array([1,2,3,4,5]); assert isinstance(ethical_primality_test(5,E,x), bool); print('OK')"

# 2) Dry-run (no API)
python scripts/llm_stress_test.py --num-actions 5 --dry-run --output-dir llm_stress_test_results

# 3) Unit tests for Phase 1
python -m pytest tests/test_erh_phase1.py -v
```

**Note:** If your terminal can’t be operated manually or automation times out, run Option A (or B) from another environment (e.g. VS Code terminal, WSL, or CI) and confirm 0 failures / “All three verifications passed” before merging.

---

## 4. Linter / code quality

- **ethical_primes.py:** Many SonarQube warnings are naming (e.g. `Pi_x`, `E_x`, `X_max`) – kept for math convention; no change.
- **ethical_primality_test:** `np.where(cond)[0]` replaced with `np.flatnonzero(cond)` per linter.
- **llm_stress_test.py:** Unused import `evaluate_judgement` removed. Remaining warnings: cognitive complexity, parameter count, and math-style names – acceptable for this script.

---

## 5. Security

- API keys: Used only via GitHub Secrets (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`); not logged or written to repo.
- Script: Reads keys from env; no hardcoding.

---

## 6. Recommendations

1. **Run verification commands above** before merge/PR (verification-before-completion).
2. **CI:** Workflow runs small-scale (100) when a key is set; without key runs dry-run – no change needed unless you want 10k in CI.
3. **Optional:** Add `llm_stress_test_Pi_E.png` to `scripts/integrate_figures.py` figure map if you want it auto-inserted into LaTeX by that script.
4. **Optional:** Add `requests` to `requirements.txt` so local runs match CI without an extra `pip install` in the workflow.

---

## 7. Bottom line

Implementation matches the plan and workflow requirements. Fixes applied: `np.flatnonzero`, remove unused import, add Phase 1 unit tests. Complete the verification steps above and then treat Phase 1 + workflow as done.
