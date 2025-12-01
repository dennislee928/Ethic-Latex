"""
Generate a synthetic exam cheating dataset for ERH case study.

Outputs: data/exam_cheating_cases.csv
Schema (compatible with exam_cheating_case_study.py):
- cheated (int, 0/1 target)
- region (categorical)
- country (categorical)
- subject_count, avg_score, score_std, time_per_question,
  suspicious_similarity, proctor_flags (numeric / categorical)
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "exam_cheating_cases.csv"


def _sample_exam_cheating(n: int = 4000, seed: int = 123) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    regions = ["Asia", "Europe", "Americas", "Africa", "Oceania"]
    countries = ["A", "B", "C", "D", "E"]

    region = rng.choice(regions, size=n)
    country = rng.choice(countries, size=n)

    subject_count = rng.integers(3, 8, size=n)
    avg_score = rng.normal(70, 15, size=n).clip(0, 100)
    score_std = rng.normal(10, 5, size=n).clip(1, 30)
    time_per_question = rng.normal(60, 20, size=n).clip(20, 200)

    suspicious_similarity = rng.beta(2, 8, size=n)  # mostly low similarity
    # Some regions / centers have higher base suspicion
    suspicious_similarity += 0.2 * (region == "Asia").astype(float)
    suspicious_similarity += 0.2 * (country == "A").astype(float)
    suspicious_similarity = suspicious_similarity.clip(0, 1)

    proctor_flags = rng.binomial(1, 0.05 + 0.25 * suspicious_similarity)

    # Logistic model for cheating probability
    logit = (
        -3.0
        + 4.0 * suspicious_similarity
        + 0.8 * proctor_flags
        + 0.01 * (avg_score - 70)
        - 0.02 * (time_per_question - 60)
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    cheated = rng.binomial(1, prob)

    df = pd.DataFrame(
        {
            "region": region,
            "country": country,
            "subject_count": subject_count,
            "avg_score": avg_score.round(1),
            "score_std": score_std.round(1),
            "time_per_question": time_per_question.round(1),
            "suspicious_similarity": suspicious_similarity.round(3),
            "proctor_flags": proctor_flags,
            "cheated": cheated,
        }
    )
    return df


def generate_synthetic_exam_cheating(n: int = 4000, overwrite: bool = True) -> Tuple[Path, int]:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DATA_PATH.exists() and not overwrite:
        df = pd.read_csv(DATA_PATH)
        return DATA_PATH, len(df)

    df = _sample_exam_cheating(n=n)
    df.to_csv(DATA_PATH, index=False)
    return DATA_PATH, len(df)


def main() -> None:
    path, n = generate_synthetic_exam_cheating()
    print(f"[generate_synthetic_exam_cheating] Wrote {n} rows to {path}")


if __name__ == "__main__":  # pragma: no cover
    main()


