"""
Medical triage real-data case study for the Ethical Riemann Hypothesis.

The intended real dataset is UCI Heart Disease, but this module is designed
to run in offline environments with injected or stub data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Tuple
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.real_data.compas_case_study import calculate_cumulative_error, fit_power_law

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
except ImportError:  # pragma: no cover - handled by fallback path
    LogisticRegression = None  # type: ignore
    train_test_split = None  # type: ignore
    StandardScaler = None  # type: ignore

DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "heart_disease.csv"

DEFAULT_NORMAL_RANGES: Dict[str, Tuple[float, float]] = {
    "trestbps": (90.0, 140.0),
    "chol": (125.0, 240.0),
    "thalach": (100.0, 220.0),
    "oldpeak": (0.0, 2.0),
}


def _truth_from_target(target: Any) -> float:
    """Map clinical target to V(a): urgent care needed=+1, otherwise=-1."""
    return 1.0 if int(target) >= 1 else -1.0


def _importance_from_triage(level: Any) -> float:
    """Map clinical triage severity to w(a)."""
    normalized = str(level or "non_urgent").strip().lower().replace("-", "_").replace(" ", "_")
    return {
        "critical": 5.0,
        "urgent": 3.0,
        "semi_urgent": 1.5,
        "semiurgent": 1.5,
        "non_urgent": 1.0,
        "nonurgent": 1.0,
    }.get(normalized, 1.0)


def _complexity_from_clinical(row: pd.Series, normal_ranges: Mapping[str, Tuple[float, float]]) -> int:
    """
    Complexity from abnormal vitals/labs plus feature density.
    """
    n_abnormal = 0
    for col, (lo, hi) in normal_ranges.items():
        if col not in row or pd.isna(row[col]):
            continue
        value = float(row[col])
        if not (lo <= value <= hi):
            n_abnormal += 1

    n_features = sum(1 for value in row.values if pd.notna(value))
    raw = n_abnormal * 10 + n_features
    return int(np.clip(raw, 1, 100))


def _load_medical_data(data_path: Path | None = None) -> pd.DataFrame:
    path = (data_path or DEFAULT_DATA_PATH).resolve()
    if path.exists():
        return pd.read_csv(path).dropna().reset_index(drop=True)
    return _stub_medical_data()


def _stub_medical_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [63, 41, 55, 38, 70, 45, 60, 50, 66, 47, 59, 43],
            "trestbps": [160, 120, 145, 118, 170, 125, 150, 122, 155, 130, 148, 116],
            "chol": [280, 190, 260, 180, 310, 205, 250, 195, 275, 210, 258, 185],
            "thalach": [95, 175, 120, 180, 88, 165, 110, 172, 105, 160, 118, 176],
            "oldpeak": [3.1, 0.2, 2.2, 0.1, 4.0, 0.5, 2.8, 0.3, 3.4, 0.4, 2.4, 0.2],
            "triage_level": [
                "critical",
                "non_urgent",
                "urgent",
                "non_urgent",
                "critical",
                "semi_urgent",
                "urgent",
                "non_urgent",
                "critical",
                "semi_urgent",
                "urgent",
                "non_urgent",
            ],
            "target": [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0],
        }
    )


def _feature_columns(df: pd.DataFrame) -> list[str]:
    excluded = {"target", "num", "triage_level"}
    return [col for col in df.select_dtypes(include=[np.number]).columns if col not in excluded]


def _clinical_risk_probability(df: pd.DataFrame) -> np.ndarray:
    complexities = np.array(
        [_complexity_from_clinical(row, DEFAULT_NORMAL_RANGES) for _, row in df.iterrows()],
        dtype=float,
    )
    if complexities.max() <= complexities.min():
        return np.full(len(df), 0.5)
    return np.clip((complexities - complexities.min()) / (complexities.max() - complexities.min()), 0.05, 0.95)


def _logistic_or_fallback_predictions(df: pd.DataFrame, target: np.ndarray) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """
    Return evaluated rows, true labels, and urgent-care probabilities.
    """
    features = _feature_columns(df)
    if len(df) < 30 or not features or LogisticRegression is None or train_test_split is None or StandardScaler is None:
        return df, target, _clinical_risk_probability(df)

    class_counts = pd.Series(target).value_counts()
    stratify = target if len(class_counts) > 1 and class_counts.min() >= 2 else None
    test_size = 0.3 if len(df) >= 10 else 0.5

    try:
        x_train, x_test, y_train, y_test, idx_train, idx_test = train_test_split(
            df[features].values,
            target,
            np.arange(len(df)),
            test_size=test_size,
            random_state=42,
            stratify=stratify,
        )
        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train)
        x_test_scaled = scaler.transform(x_test)
        model = LogisticRegression(max_iter=1000, class_weight="balanced")
        model.fit(x_train_scaled, y_train)
        probs = model.predict_proba(x_test_scaled)[:, 1]
        return df.iloc[idx_test].reset_index(drop=True), y_test, probs
    except Exception:
        return df, target, _clinical_risk_probability(df)


def run_medical_triage_erh_analysis(
    df: pd.DataFrame | None = None,
    data_path: Path | None = None,
) -> Dict[str, Any]:
    """
    Run ERH analysis for a clinical triage classifier.
    """
    clinical_df = (df.copy() if df is not None else _load_medical_data(data_path)).dropna().reset_index(drop=True)
    target_col = "target" if "target" in clinical_df.columns else "num" if "num" in clinical_df.columns else None
    if target_col is None:
        return {"error": "Medical dataset requires a target or num column"}

    target = (clinical_df[target_col].astype(int).values >= 1).astype(int)
    eval_df, y_eval, probs = _logistic_or_fallback_predictions(clinical_df, target)

    truth = np.array([_truth_from_target(value) for value in y_eval], dtype=float)
    judgment = np.clip((2.0 * probs) - 1.0, -1.0, 1.0)
    complexity = np.array(
        [_complexity_from_clinical(row, DEFAULT_NORMAL_RANGES) for _, row in eval_df.iterrows()],
        dtype=int,
    )
    weights = np.array(
        [_importance_from_triage(row.get("triage_level", "non_urgent")) for _, row in eval_df.iterrows()],
        dtype=float,
    )

    x_vals, E_x = calculate_cumulative_error(truth * weights, judgment * weights, complexity, x_max=100)
    alpha, C = fit_power_law(x_vals, E_x, x_min=10)
    alpha = float(np.clip(alpha, 0.0, 1.5))
    predicted = np.where(judgment >= 0.0, 1.0, -1.0)
    mistakes = predicted != truth
    n_total = int(len(truth))
    n_mistakes = int(mistakes.sum())

    return {
        "case_name": "medical_triage",
        "alpha": float(alpha),
        "C": float(C),
        "erh_satisfied": bool(alpha < 0.6),
        "n_total": n_total,
        "n_mistakes": n_mistakes,
        "mistake_rate": float(n_mistakes / n_total) if n_total else 0.0,
        "x": x_vals.tolist(),
        "E_x": E_x.tolist(),
    }


if __name__ == "__main__":  # pragma: no cover
    result = run_medical_triage_erh_analysis()
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Medical triage alpha: {result['alpha']:.4f}")
        print(f"  ERH satisfied: {result['erh_satisfied']}")
        print(f"  Mistake rate: {result['mistake_rate']:.2%} ({result['n_mistakes']}/{result['n_total']})")
