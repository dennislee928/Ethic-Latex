"""
COMPAS recidivism real-data case study for the Ethical Riemann Hypothesis (ERH).

Applies ERH-style error growth analysis to the ProPublica COMPAS dataset.
Expects compas-scores-two-years.csv or similar format in data/ folder.
Fails gracefully if data is unavailable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

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


def load_compas_data(csv_path: Path | None = None) -> pd.DataFrame:
    """
    Load and cleanse COMPAS data. Alias for load_compas_dataset with enhanced cleansing.
    Handles missing values for decile_score and two_year_recid.
    """
    path = csv_path or DEFAULT_DATA_PATH
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(
            f"COMPAS CSV not found at {path}. "
            "Place compas-scores-two-years.csv under data/ to enable this case study."
        )
    df = pd.read_csv(path)
    # Require columns
    if "two_year_recid" not in df.columns or "decile_score" not in df.columns:
        raise ValueError("Expected columns 'two_year_recid' and 'decile_score' in COMPAS data.")
    # Cleanse: drop rows with missing values in key columns
    df = df.dropna(subset=["two_year_recid", "decile_score"]).reset_index(drop=True)
    # Cleanse: clamp decile_score to valid range 1-10
    df["decile_score"] = df["decile_score"].clip(1, 10)
    return df


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


def _ground_truth_from_recid(two_year_recid: np.ndarray) -> np.ndarray:
    """Map two_year_recid (0/1) to Ethical Value V(a) in (-1, +1). recid=0 → +1, recid=1 → -1."""
    return np.where(two_year_recid == 0, 1.0, -1.0)


def _agent_judgment_from_decile(decile_score: np.ndarray) -> np.ndarray:
    """Map decile_score (1-10) to normalized judgment in [-1, +1]. decile 1→-1, 10→+1."""
    arr = decile_score.values if hasattr(decile_score, "values") else np.asarray(decile_score)
    return np.clip((arr - 5.5) / 4.5, -1.0, 1.0)


def _complexity_from_priors(df: pd.DataFrame) -> np.ndarray:
    """Complexity x from priors_count (criminal history length) + feature density."""
    if {"priors_count", "c_charge_degree", "days_b_screening_arrest"}.issubset(df.columns):
        return _complexity_from_charge(df).to_numpy()

    if "priors_count" in df.columns:
        priors = df["priors_count"].fillna(0).values.astype(float)
    else:
        priors = np.zeros(len(df))
    n_feat = len(df.select_dtypes(include=[np.number]).columns) if len(df) > 0 else 1
    raw = np.clip(priors + 0.1 * n_feat, 1, 100)
    if raw.max() <= raw.min():
        return np.ones(len(df), dtype=int)
    return (1 + 99 * (raw - raw.min()) / (raw.max() - raw.min() + 1e-8)).astype(int)


def _complexity_from_charge(df: pd.DataFrame) -> pd.Series:
    """
    Richer COMPAS complexity from priors, charge severity, and screening lag.

    Felony charges and delayed screening are treated as higher-complexity
    contexts, then normalized to integer bins in [1, 100].
    """
    priors = df.get("priors_count", pd.Series(np.zeros(len(df)), index=df.index)).fillna(0).astype(float)
    charge = (
        df.get("c_charge_degree", pd.Series(["M"] * len(df), index=df.index))
        .map({"F": 2, "M": 1})
        .fillna(1)
        .astype(float)
    )
    screening_days = (
        df.get("days_b_screening_arrest", pd.Series(np.zeros(len(df)), index=df.index))
        .fillna(0)
        .astype(float)
        .abs()
    )
    urgency = (screening_days > 7).astype(float) * 2.0
    raw = priors + charge * 3.0 + urgency
    if raw.max() <= raw.min():
        return pd.Series(np.ones(len(df), dtype=int), index=df.index)
    scaled = 1 + 99 * (raw - raw.min()) / (raw.max() - raw.min() + 1e-8)
    return scaled.astype(int)


def calculate_cumulative_error(
    truth: np.ndarray,
    judgment: np.ndarray,
    complexity: np.ndarray,
    x_max: int = 100,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute E(x) = sum(Judgment - Truth) for all points with complexity <= x.

    Returns
    -------
    x_values : np.ndarray
        Complexity bins 1..x_max.
    E_x : np.ndarray
        Cumulative error at each x.
    """
    x_vals = np.arange(1, x_max + 1, dtype=float)
    err = judgment - truth
    E_x = np.array([float(err[complexity <= x].sum()) for x in x_vals])
    return x_vals, E_x


def fit_power_law(x: np.ndarray, E_x: np.ndarray, x_min: int = 10) -> Tuple[float, float]:
    """
    Fit |E(x)| ~ C * x^alpha using scipy.optimize.curve_fit.

    Returns
    -------
    alpha : float
        Power law exponent.
    C : float
        Scale constant.
    """
    try:
        from scipy.optimize import curve_fit
    except ImportError:
        # Fallback: polyfit in log-log
        mask = (x >= x_min) & (np.abs(E_x) > 1e-12)
        if mask.sum() < 2:
            return 0.0, 1.0
        log_x = np.log(x[mask])
        log_e = np.log(np.abs(E_x[mask]) + 1e-8)
        coeffs = np.polyfit(log_x, log_e, 1)
        alpha = float(coeffs[0])
        C = float(np.exp(coeffs[1]))
        return alpha, C

    def _power_law(x_arr: np.ndarray, c: float, a: float) -> np.ndarray:
        return c * np.power(x_arr, a)

    mask = (x >= x_min) & (np.abs(E_x) > 1e-12)
    if mask.sum() < 2:
        return 0.0, 1.0
    x_fit = x[mask]
    y_fit = np.abs(E_x[mask]) + 1e-8
    try:
        popt, _ = curve_fit(_power_law, x_fit, y_fit, p0=[1.0, 0.5], maxfev=5000)
        return float(popt[1]), float(popt[0])
    except Exception:
        return 0.0, 1.0


def run_compas_erh_analysis(data_path: Path | None = None) -> Dict[str, Any]:
    """
    Run ERH-style analysis on COMPAS: Ground Truth, Judgment, Complexity, E(x), alpha.
    Returns dict with x, E_x, alpha, C, or error key if failed.
    """
    path = (data_path or DEFAULT_DATA_PATH).resolve()
    if not path.exists():
        return {"error": "COMPAS CSV not found"}
    try:
        df = load_compas_data(path)
        truth = _ground_truth_from_recid(df["two_year_recid"].values)
        judgment = _agent_judgment_from_decile(df["decile_score"])
        complexity = _complexity_from_priors(df)
        x_vals, E_x = calculate_cumulative_error(truth, judgment, complexity)
        alpha, C = fit_power_law(x_vals, E_x)
        return {"x": x_vals.tolist(), "E_x": E_x.tolist(), "alpha": alpha, "C": C}
    except Exception as e:
        return {"error": str(e)}


def _compas_group_result(group_name: str, df: pd.DataFrame) -> Dict[str, Any]:
    truth = _ground_truth_from_recid(df["two_year_recid"].values)
    judgment = _agent_judgment_from_decile(df["decile_score"])
    complexity = _complexity_from_priors(df)
    x_vals, E_x = calculate_cumulative_error(truth, judgment, complexity)
    alpha, C = fit_power_law(x_vals, E_x)
    alpha = float(np.clip(alpha, 0.0, 1.5))
    predicted = np.where(judgment >= 0.0, 1.0, -1.0)
    mistakes = predicted != truth
    n_total = int(len(df))
    n_mistakes = int(mistakes.sum())
    return {
        "group": group_name,
        "alpha": float(alpha),
        "C": float(C),
        "erh_satisfied": bool(alpha < 0.6),
        "n_total": n_total,
        "n_mistakes": n_mistakes,
        "mistake_rate": float(n_mistakes / n_total) if n_total else 0.0,
        "x": x_vals.tolist(),
        "E_x": E_x.tolist(),
    }


def run_compas_by_race(df: pd.DataFrame | None = None, data_path: Path | None = None) -> Dict[str, Any]:
    """
    Run COMPAS ERH analysis separately per race group.

    Returns alpha and standard ERH summary fields for each group, allowing
    direct comparison of whether errors compound differently by race.
    """
    if df is None:
        path = (data_path or DEFAULT_DATA_PATH).resolve()
        if not path.exists():
            return {"error": "COMPAS CSV not found"}
        df = load_compas_data(path)

    required = {"race", "two_year_recid", "decile_score"}
    missing = required.difference(df.columns)
    if missing:
        return {"error": f"Missing required columns: {sorted(missing)}"}

    groups: Dict[str, Any] = {}
    for race in sorted(str(r) for r in df["race"].dropna().unique()):
        sub = df[df["race"].astype(str) == race].reset_index(drop=True)
        if sub.empty:
            continue
        groups[race] = _compas_group_result(race, sub)

    return {
        "case_name": "compas_by_race",
        "n_groups": len(groups),
        "groups": groups,
    }


def run_compas_alpha(
    data_path: Path | None = None,
) -> float | None:
    """
    Compute alpha for COMPAS baseline model.
    Returns None if dataset or sklearn unavailable.
    """
    path = (data_path or DEFAULT_DATA_PATH).resolve()
    if LogisticRegression is None or not path.exists():
        return None
    try:
        df = load_compas_dataset(data_path)
        X, y, complexities = preprocess_compas(df)
        alpha, _, _ = fit_and_evaluate_compas(X, y, complexities)
        return alpha
    except Exception:
        return None
