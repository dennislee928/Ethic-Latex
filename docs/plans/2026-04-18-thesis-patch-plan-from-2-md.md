# Thesis Patch Plan From `.ignore_ref/2.md`

**Date:** 2026-04-18

## Goal

Turn the review note in `.ignore_ref/2.md` into an actionable thesis-revision plan that improves clarity, internal consistency, empirical credibility, and practical relevance without bloating the paper into an unbounded rewrite.

## Primary Targets

- `latex/ethical_riemann_hypothesis.tex`
- `latex/ethical_riemann_hypothesis_en.tex`
- `latex/ethical_riemann_hypothesis_zh.tex`
- `latex/references.bib`
- Generated figure/table inputs under `simulation/output/` and `figures/` only where thesis claims or captions must be corrected to match the source results

## Source Synthesis

The note in `.ignore_ref/2.md` is not a single bug report. It is a mixed critique containing four useful signals:

- The paper's core idea is strong: dynamic structural error growth is a meaningful contribution beyond static fairness metrics.
- The current real-world case-study writeup is not clear enough for non-specialists, especially around what the reported `\alpha` values imply in practice.
- There are likely internal consistency problems, especially around COMPAS `\alpha` values, table wording, and presentation artifacts.
- The paper has a credible future-work pipeline, but it needs prioritization and separation between what this version proves, what it demonstrates, and what it only proposes.

## Patch Objectives

1. Remove contradictions and low-trust presentation defects.
2. Make the Adult Income and COMPAS case studies readable as practical conclusions rather than only mathematical diagnostics.
3. Translate ERH outputs into decision guidance while keeping the paper honest about scope.
4. Reframe future work so it strengthens the contribution instead of overextending the claims.
5. Keep the English and Chinese thesis variants aligned on the same core claims and numbers.

## Workstream 1: Consistency Audit And Repairs

### Why

The note flags credibility-damaging inconsistencies. These are the highest-priority fixes because they weaken every stronger claim in the manuscript.

### Patch Tasks

- Reconcile every reported COMPAS exponent across abstract, results, captions, tables, and conclusion.
  - Current conflict observed in source: `latex/ethical_riemann_hypothesis.tex` reports COMPAS as `-0.20` in the abstract and case-study summary, while `.ignore_ref/2.md` also references a `-0.32` value and a figure-label mismatch.
- Verify whether Adult Income, COMPAS, and synthetic-judge `\alpha` values match the generated plots and table rows.
- Fix any truncated or placeholder table content.
  - The note specifically calls out an "Overall verdict" field that appears clipped.
- Confirm that complexity-range descriptions match the actual experimental setup.
  - The note suggests a mismatch between low-level counts and the declared `[1, 100]` range.
- Add a short explanation wherever negative `\alpha` values are introduced, clarifying that "`\alpha < 0.5` satisfies the ERH-style upper bound" does not mean "the system is fair" or "better in every sense."

### Likely Files

- `latex/ethical_riemann_hypothesis.tex`
- `latex/ethical_riemann_hypothesis_en.tex`
- `latex/ethical_riemann_hypothesis_zh.tex`
- Any generated LaTeX fragments consumed by thesis tables or figures

### Done Criteria

- One authoritative value per metric per dataset.
- No abstract/body/figure/table contradictions remain.
- No visible placeholder or clipped wording survives in thesis tables.

## Workstream 2: Rewrite The Real-World Case-Study Inference

### Why

The note's strongest criticism is not that the framework fails, but that the conclusions stop at "the indicator works." The patch needs to explain what a reader should learn from Adult Income and COMPAS.

### Patch Tasks

- Rewrite the Adult Income subsection around a plain-language claim:
  - mitigation reduced both pointwise error and structural error accumulation;
  - ERH complements, rather than replaces, group fairness metrics.
- Rewrite the COMPAS subsection around a plain-language claim:
  - structural stability does not equal fairness;
  - the result shows bounded long-tail error growth, not moral acceptability.
- Add one compact interpretation block after each case study:
  - `Observed signal`
  - `What ERH lets us conclude`
  - `What ERH does not let us conclude`
  - `What a system designer should inspect next`
- Tighten the language around "universality" and "predictive" claims unless the repo already contains evidence for those stronger statements.

### Likely Files

- `latex/ethical_riemann_hypothesis.tex`
- `latex/ethical_riemann_hypothesis_en.tex`
- `latex/ethical_riemann_hypothesis_zh.tex`

### Done Criteria

- A reviewer can read each case-study subsection and extract a practical takeaway without reverse-engineering the math.
- The paper clearly distinguishes diagnosis, interpretation, and prescription.

## Workstream 3: Add A Practical ERH Interpretation Layer

### Why

The note repeatedly points to a diagnosis-to-action gap. The paper can close much of that gap with framing, even if it does not yet implement a full intervention algorithm.

### Patch Tasks

- Add a short subsection mapping exponent regimes to operational interpretations.
  - Example structure: `\alpha > 0.5`, near-critical `\alpha \approx 0.5`, low-positive, near-zero, and negative regimes.
- State clearly that ERH is a necessary structural-health condition, not a sufficiency result.
- Add a recommended "dual-metric" reading rule:
  - stability metric (`\alpha`, bounded normalized oscillation)
  - task metric (accuracy, calibration, fairness gap, or domain-specific loss)
- Where claims about early warning or monitoring remain speculative, label them as a design proposal rather than an established empirical result.

### Likely Files

- `latex/ethical_riemann_hypothesis.tex`
- `latex/ethical_riemann_hypothesis_en.tex`
- `latex/ethical_riemann_hypothesis_zh.tex`

### Done Criteria

- The paper gives readers an interpretation schema for ERH outputs.
- "Healthy," "stable," and "fair" are no longer conflated.

## Workstream 4: Narrow And Prioritize Empirical Expansion

### Why

`.ignore_ref/2.md` lists roughly twenty possible domains. That is useful as a research backlog, but too diffuse for a thesis patch unless it is ranked and scoped.

### Patch Tasks

- Replace any raw long list with a prioritized shortlist of `3-5` expansion domains.
- Rank candidate domains by:
  - high decision stakes
  - clear complexity proxy
  - public or reproducible data availability
  - interpretability for non-specialist readers
- Recommended shortlist for the patched thesis:
  - medical triage
  - content moderation / hate-speech review
  - education admissions or essay scoring
  - welfare or benefit eligibility screening
  - safety-critical autonomy only if data and evaluation design are defensible
- Frame the larger twenty-domain set as an appendix or internal roadmap, not as promised near-term validation.

### Done Criteria

- Future empirical work reads as a credible roadmap, not an unbounded wish list.
- The next validation step is obvious.

## Workstream 5: Tighten Theoretical Positioning

### Why

The note contains good theoretical ideas, but several belong in "future work" rather than the paper's current claim set.

### Patch Tasks

- Sharpen the limitation text around:
  - heuristic status of the ethical-zeta analogy;
  - finite-sum rather than full analytic-number-theory machinery;
  - subjectivity in importance weighting and ethical-prime selection.
- Add a structured future-work subsection that groups extensions instead of scattering them.
  - algebraic/topological definition of ethical primes
  - ERH regularization during training
  - adversarial ethical primes
  - dynamic ERH / drift monitoring
  - multi-dimensional ethical zeta
  - human-in-the-loop ERH
- Keep each item in proposal mode unless the repository already contains implementational evidence.

### Likely Files

- `latex/ethical_riemann_hypothesis.tex`
- `latex/ethical_riemann_hypothesis_en.tex`
- `latex/ethical_riemann_hypothesis_zh.tex`
- `latex/references.bib` if new citations are added

### Done Criteria

- The contribution boundary is explicit.
- The paper sounds more rigorous because it separates validated results from research directions.

## Workstream 6: Figure And Table Sync

### Why

Several issues in the note appear to be generated-artifact mismatches rather than prose-only problems.

### Patch Tasks

- Audit all figure captions and legend text that mention `\alpha`, ERH adherence, or structural similarity.
- Rebuild any generated comparison tables if they still emit stale values or clipped labels.
- Ensure English and Chinese captions express the same claim strength.
- Remove or soften captions that overstate universality, prediction, or fairness conclusions.

### Likely Files

- Thesis `.tex` files
- `simulation/output/figures_latex_code.tex`
- `simulation/output/figures/comparison_table_rows.tex`
- Figure-generation scripts only if stale outputs cannot be corrected at the LaTeX layer

### Done Criteria

- Captions match plots.
- Tables render completely.
- No figure legend carries a stronger claim than the body text supports.

## Suggested Execution Order

1. Consistency audit and numeric reconciliation.
2. Case-study rewrite.
3. ERH interpretation-layer insert.
4. Theory/future-work restructuring.
5. Figure/table synchronization.
6. Cross-language alignment pass.

## Verification Checklist

- Run a targeted grep for every reported COMPAS and Adult `\alpha` value across the thesis sources.
- Build the thesis PDFs and inspect warnings related to missing figures, overfull boxes, or table rendering.
- Manually inspect the abstract, case-study sections, alpha-comparison table, and relevant captions in all language variants.
- Confirm that every "predictive," "universal," or "design criterion" claim is backed either by evidence in the repo or marked as a proposal/interpretation.

## Out Of Scope For This Patch

- Adding all twenty proposed case studies.
- Claiming causal mechanisms that the current experiments do not identify.
- Turning ERH into a fully operational training-time regularizer unless code and experiments are added.
- Making stronger fairness claims from structural-stability evidence alone.

## Expected Outcome

After this patch, the thesis should read as a more disciplined research artifact: internally consistent, clearer about what the real-world cases show, more honest about what ERH can and cannot conclude, and better positioned for a second-stage empirical expansion.
