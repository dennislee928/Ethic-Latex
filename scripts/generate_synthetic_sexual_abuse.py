"""
Generate a synthetic sexual abuse reporting dataset for ERH case study.

Outputs: data/sexual_abuse_cases.csv
Schema (compatible with sexual_abuse_case_study.py):
- reported (int, 0/1 target)
- gender (categorical)
- age_group, relationship_to_offender, incident_context,
  support_services_available, prior_reports_count, severity_score.

This is a purely synthetic example intended for methodological illustration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "sexual_abuse_cases.csv"


def _sample_sexual_abuse(n: int = 3000, seed: int = 456) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    genders = ["Female", "Male", "Non-binary"]
    gender = rng.choice(genders, size=n, p=[0.6, 0.35, 0.05])

    age_groups = ["<18", "18-24", "25-34", "35-49", "50+"]
    age_group = rng.choice(age_groups, size=n, p=[0.25, 0.3, 0.2, 0.15, 0.1])

    relationships = ["stranger", "acquaintance", "family", "authority"]
    relationship_to_offender = rng.choice(relationships, size=n, p=[0.25, 0.35, 0.25, 0.15])

    contexts = ["school", "workplace", "home", "online", "public"]
    incident_context = rng.choice(contexts, size=n)

    support_services_available = rng.binomial(1, 0.4, size=n)
    prior_reports_count = rng.poisson(0.2, size=n)

    # Severity score: higher for authority/family, certain contexts, and young age groups.
    base_severity = rng.beta(2, 3, size=n)
    base_severity += 0.3 * (relationship_to_offender == "authority").astype(float)
    base_severity += 0.2 * (relationship_to_offender == "family").astype(float)
    base_severity += 0.2 * (incident_context == "home").astype(float)
    base_severity += 0.1 * (age_group == "<18").astype(float)
    severity_score = base_severity.clip(0, 1)

    # Reporting probability:
    # - higher when severity is high and support is available
    # - lower when offender is family and support is absent
    logit = (
        -1.5
        + 3.0 * severity_score
        + 0.8 * support_services_available
        - 0.5 * (relationship_to_offender == "family").astype(float) * (1 - support_services_available)
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    reported = rng.binomial(1, prob)

    df = pd.DataFrame(
        {
            "gender": gender,
            "age_group": age_group,
            "relationship_to_offender": relationship_to_offender,
            "incident_context": incident_context,
            "support_services_available": support_services_available,
            "prior_reports_count": prior_reports_count,
            "severity_score": severity_score.round(3),
            "reported": reported,
        }
    )
    return df


def generate_synthetic_sexual_abuse(n: int = 3000, overwrite: bool = True) -> Tuple[Path, int]:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DATA_PATH.exists() and not overwrite:
        df = pd.read_csv(DATA_PATH)
        return DATA_PATH, len(df)

    df = _sample_sexual_abuse(n=n)
    df.to_csv(DATA_PATH, index=False)
    return DATA_PATH, len(df)


def main() -> None:
    path, n = generate_synthetic_sexual_abuse()
    print(f"[generate_synthetic_sexual_abuse] Wrote {n} rows to {path}")


if __name__ == "__main__":  # pragma: no cover
    main()


