"""
COMPAS recidivism real-data case study for the Ethical Riemann Hypothesis (ERH).

Applies ERH-style error growth analysis to the ProPublica COMPAS dataset.
Expects compas-scores-two-years.csv or similar format in data/ folder.
Fails gracefully if data is unavailable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
except ImportError:
    LogisticRegression = None
    train_test_split = None
    StandardScaler = None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "compas-scores-two-years.csv"


def load_compas_dataset(csv_path: Path | None = None) -> pd.DataFrame:
    """Load COMPAS dataset. Expects ProPublica format."""
    path = csv_path or DEFAULT_DATA_PATH
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(
            f"COMPAS CSV not found at {path}. "
            "Place compas-scores-two-years.csv under data/ to enable this case study."
        )
    df = pd.read_csv(path)
    if "two_year_recid" not in df.columns or "decile_score" not in df.columns:
        raise ValueError("Expected columns 'two_year_recid' and 'decile_score' in COMPAS data.")
    return df.dropna(subset=["two_year_recid", "decile_score"]).reset_index(drop=True)


def preprocess_compas(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract features, labels, and complexity proxy from COMPAS."""
    y = df["two_year_recid"].astype(int).values
    decile = df["decile_score"].values / 10.0

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    drop_cols = {"two_year_recid", "decile_score", "id"}
    feature_cols = [c for c in numeric_cols if c not in drop_cols]

    if len(feature_cols) == 0:
        X = decile.reshape(-1, 1)
    else:
        X_raw = df[feature_cols].fillna(0).values
        X = np.hstack([decile.reshape(-1, 1), X_raw])

    if StandardScaler is not None:
        X = StandardScaler().fit_transform(X)

    complexity = np.clip(1 + 99 * (decile - decile.min()) / (decile.max() - decile.min() + 1e-8), 1, 100).astype(int)
    return X, y, complexity


def fit_and_evaluate_compas(
    X: np.ndarray, y: np.ndarray, complexities: np.ndarray
) -> Tuple[float, np.ndarray, np.ndarray]:
    """Fit logistic regression on COMPAS, return alpha, errors, complexities."""
    if LogisticRegression is None or train_test_split is None:
        raise ImportError("scikit-learn required for COMPAS case study.")

    X_train, X_test, y_train, y_test, c_train, c_test = train_test_split(
        X, y, complexities, test_size=0.3, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    errors = preds - y_test

    return _compute_alpha(errors, c_test), errors, c_test


def _compute_alpha(errors: np.ndarray, complexities: np.ndarray, x_max: int = 100) -> float:
    """Compute ERH growth exponent alpha from errors and complexities."""
    misclassified = (errors != 0).astype(int)
    x_vals = np.arange(1, x_max + 1, dtype=float)
    pi_x = np.array([int(misclassified[complexities <= x].sum()) for x in x_vals])
    with np.errstate(divide="ignore", invalid="ignore"):
        baseline_shape = x_vals / np.log1p(x_vals)
        baseline_shape[-1] = max(baseline_shape[-1], 1.0)
        scale = pi_x[-1] / baseline_shape[-1] if baseline_shape[-1] > 0 else 1.0
        b_x = scale * baseline_shape
    e_x = np.abs(pi_x - b_x)
    x0 = 10
    mask = x_vals >= x0
    if e_x[mask].sum() == 0:
        return 0.0
    log_x = np.log(x_vals[mask])
    log_e = np.log(e_x[mask] + 1e-8)
    coeffs = np.polyfit(log_x, log_e, 1)
    return float(coeffs[0])


def run_compas_alpha(
    data_path: Path | None = None,
) -> float | None:
    """
    Compute alpha for COMPAS baseline model.
    Returns None if dataset or sklearn unavailable.
    """
    if LogisticRegression is None or not (data_path or DEFAULT_DATA_PATH).resolve().exists():
        return None
    try:
        df = load_compas_dataset(data_path)
        X, y, complexities = preprocess_compas(df)
        alpha, _, _ = fit_and_evaluate_compas(X, y, complexities)
        return alpha
    except Exception:
        return None
