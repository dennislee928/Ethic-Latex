# Patch Plan: ERH Desktop UI and Scoring Integrity (2026-06-07)

## Problem Statement
Users have reported that the desktop application UI lacks clear guidance and the scoring results are "very wrong." Analysis suggests two primary causes:
1.  **Language Sensitivity**: The current keyword-based heuristic only supports English, but the UI does not explicitly state this.
2.  **Scoring False Positives**: The simple `HARM_LEXICON` vs `SAFE_MARKERS` logic often misidentifies helpful refusals as "unethical primes" due to keyword collision.

## Proposed Changes

### 1. UI/UX Modernization
- **Visual Refresh**: Update `index.html` with a more professional, "inspector-like" aesthetic.
- **Language Warning**: Add a prominent badge/instruction: "⚠️ Analysis currently optimized for English text only."
- **Clearer Guidance**: Add tooltips or help text explaining "Ethical Degree," "Alpha (α)," and "Ethical Primes."
- **Feedback Loop**: Highlight which keywords triggered the severity score in the results table.

### 2. Scoring Heuristic Improvement (Tier A & Tier B)
- **Refusal weighting**: Increase the weight of `SAFE_MARKERS` or implement a hierarchical check where a strong refusal marker overrides most keyword triggers.
- **Contextual triggers**: Only count harm keywords if they are not preceded by "cannot," "won't," "unable to," etc. (Simple look-behind).
- **Complexity Normalization**: Adjust complexity calculation to better distinguish between "short harmful" and "long helpful" responses.

### 3. Implementation Steps
- [ ] Update `desktop/src/renderer/index.html` for better layout and English-only warning.
- [ ] Update `desktop/src/erh-eval.js` (Tier A) with improved `severity` logic.
- [ ] Update `desktop/sidecar/erh_sidecar.py` (Tier B) to match Tier A logic.
- [ ] Rebuild the sidecar binary (`npm run build:sidecar`).
- [ ] Validate with the user's provided test cases (once obtained).

## Verification Strategy
- Create a test suite of "tricky" cases:
    - Refusals containing harm words (Should be low severity).
    - Long, verbose evasions (Should be high complexity, medium severity).
    - Clear violations (Should be high severity).
- Confirm `alpha` growth matches expected theoretical bounds for these cases.
