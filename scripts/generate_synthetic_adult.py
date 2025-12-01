"""
Generate a synthetic Adult Income-style dataset for ERH real-data case study.

The goal is to create a small, anonymized CSV under data/adult.csv with a
schema compatible with simulation/real_data/adult_income_case_study.py:
- income (target, >50K / <=50K)
- mix of numeric and categorical features, including sex for group analysis.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "adult.csv"


def _sample_adult(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Numeric features
    age = rng.integers(18, 70, size=n)
    hours_per_week = rng.normal(40, 10, size=n).clip(10, 80)
    capital_gain = rng.exponential(500, size=n)
    capital_loss = rng.exponential(200, size=n)

    # Categorical features
    education_levels = [
        "HS-grad",
        "Some-college",
        "Bachelors",
        "Masters",
        "Doctorate",
    ]
    education = rng.choice(education_levels, size=n, p=[0.35, 0.3, 0.25, 0.08, 0.02])

    occupations = [
        "adm-clerical",
        "craft-repair",
        "exec-managerial",
        "prof-specialty",
        "sales",
        "service",
        "other",
    ]
    occupation = rng.choice(occupations, size=n)

    marital_statuses = [
        "Never-married",
        "Married",
        "Divorced",
        "Separated",
        "Widowed",
    ]
    marital_status = rng.choice(marital_statuses, size=n)

    races = ["White", "Black", "Asian-Pac-Islander", "Other"]
    race = rng.choice(races, size=n, p=[0.7, 0.15, 0.1, 0.05])

    sexes = ["Male", "Female"]
    sex = rng.choice(sexes, size=n, p=[0.5, 0.5])

    # Logistic-style income model
    # Higher age (to a point), higher education, exec/prof occupations,
    # and more hours_per_week increase income probability.
    edu_score = np.array([education_levels.index(e) for e in education])
    occ_high = np.isin(occupation, ["exec-managerial", "prof-specialty"]).astype(float)
    hours_norm = (hours_per_week - 40) / 20.0

    logit = (
        -1.0
        + 0.03 * (age - 30)
        + 0.6 * edu_score
        + 0.8 * occ_high
        + 0.5 * hours_norm
        - 0.2 * (sex == "Female").astype(float)
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    income_flag = rng.binomial(1, prob)
    income = np.where(income_flag == 1, ">50K", "<=50K")

    df = pd.DataFrame(
        {
            "age": age,
            "hours_per_week": hours_per_week.round(1),
            "capital_gain": capital_gain.round(0),
            "capital_loss": capital_loss.round(0),
            "education": education,
            "occupation": occupation,
            "marital_status": marital_status,
            "race": race,
            "sex": sex,
            "income": income,
        }
    )
    return df


def generate_synthetic_adult(n: int = 5000, overwrite: bool = True) -> Tuple[Path, int]:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DATA_PATH.exists() and not overwrite:
        df = pd.read_csv(DATA_PATH)
        return DATA_PATH, len(df)

    df = _sample_adult(n=n)
    df.to_csv(DATA_PATH, index=False)
    return DATA_PATH, len(df)


def main() -> None:
    path, n = generate_synthetic_adult()
    print(f"[generate_synthetic_adult] Wrote {n} rows to {path}")


if __name__ == "__main__":  # pragma: no cover
    main()


