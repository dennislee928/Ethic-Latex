# ERH-on-Security: Proof-of-Concept

This document describes how the ERH-on-Security prototype maps DevSecOps data
into the Ethical Riemann Hypothesis (ERH) framework.

## Overview

- **Data source**: GitLab merge requests, CI pipelines, and security scan reports
  (or synthetic mock data).
- **Storage**: SQLite database for the PoC (`DerivedMetrics` table caches ERH
  variables).
- **Domain mapping**: `backend/app/erh_security/mapping.py` converts actions
  into ERH samples `(c, V, w, J)`.
- **ERH metrics**: `backend/app/erh_security/metrics.py` adapts the existing
  ERH code (`simulation/core/ethical_primes.py`) to compute ethical primes,
  Pi/E curves, and error-growth exponents.

## Data Mapping

For each merge request:

- **Complexity** `c`:
  - Derived from `lines_changed`, `files_changed`, `services_touched`, bounded
    to `[1, 100]`.
- **Ground truth** `V(a)`:
  - Uses unresolved high-severity findings and post-incident flags.
- **Weight** `w(a)`:
  - Log-normal-like function of asset criticality and internet exposure.
- **Judgment** `J(a)`:
  - Aggregates pipeline status and human review outcome.

## API Surface

- `POST /ingestion/run?mode=mock|gitlab`
- `GET /analysis/summary?judge_type=PIPELINE|HUMAN|COMBINED`
- `GET /analysis/curves?judge_type=...`
- `GET /analysis/heatmap?judge_type=...`

See `docs/API_SPEC.md` for detailed request/response schemas.


