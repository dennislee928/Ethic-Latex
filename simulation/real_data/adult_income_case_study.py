"""
Adult Income real-data case study for the Ethical Riemann Hypothesis (ERH).

This module demonstrates how to apply the ERH framework to a small, real
dataset. The goal is not to produce a state-of-the-art classifier, but to
illustrate how ERH-style error growth analysis can complement standard
reliability and fairness metrics.

Design goals:
- Use a simple, widely known dataset (Adult Income).
- Map tabular data into the ERH pipeline (complexity, moral value, weights).
- Compare a baseline model with a simple mitigation strategy.
- Export a human-readable Markdown report summarizing the results.

The script is designed to fail gracefully in environments where the dataset
is not available. In CI, we do NOT fetch data from the internet; instead, we
expect a local CSV (e.g., data/adult.csv). If the file is missing, the
script will log a message and exit without error.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
except ImportError:  # pragma: no cover - handled gracefully at runtime
    LogisticRegression = None  # type: ignore
    train_test_split = None  # type: ignore
    StandardScaler = None  # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "adult.csv"
DEFAULT_OUTPUT_MD = PROJECT_ROOT / "simulation" / "output" / "real_data_case_study_report.md"


def _safe_resolve_output(path: Path) -> Path:
    """
    Resolve output path and ensure it stays within the project root to
    prevent path traversal issues.
    """
    resolved = path.resolve()
    root = PROJECT_ROOT.resolve()
    if not str(resolved).startswith(str(root)):
        resolved = DEFAULT_OUTPUT_MD
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def load_adult_dataset(csv_path: Path | None = None) -> pd.DataFrame:
    """
    Load the Adult Income dataset from a local CSV file.

    Parameters
    ----------
    csv_path:
        Path to the CSV file. If None, defaults to data/adult.csv under
        the project root.

    Returns
    -------
    DataFrame
        Cleaned Adult Income dataframe.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.
    """
    path = csv_path or DEFAULT_DATA_PATH
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(
            f"Adult dataset CSV not found at {path}. "
            "Place a preprocessed adult.csv file under data/ to enable the real-data case study."
        )

    df = pd.read_csv(path)
    # Expect a target column named 'income' with values like '>50K' / '<=50K'
    if "income" not in df.columns:
        raise ValueError("Expected a column 'income' in the dataset.")

    # Drop rows with missing values for simplicity
    df = df.dropna().reset_index(drop=True)
    return df


def preprocess_adult(df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """
    Preprocess Adult Income data into features, labels, and protected attribute.

    - Target: income (>50K -> 1, <=50K -> 0)
    - Protected attribute: sex (if available), used only for group-wise reporting.
    - Complexity proxy: derived later from feature representation and model scores.
    """
    y = (df["income"].astype(str).str.contains(">50K")).astype(int).values

    # Keep a protected attribute for fairness-style reporting, if available
    if "sex" in df.columns:
        protected = df["sex"].astype(str)
    else:
        # Fallback: create a dummy group
        protected = pd.Series(["unknown"] * len(df), name="sex")

    # Basic feature selection: drop target and obvious identifiers
    drop_cols = {"income"}
    x_df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # One-hot encode categoricals; leave numerics as-is
    x_processed = pd.get_dummies(x_df, drop_first=True)
    return x_processed, y, protected


def fit_logistic_models(
    X: pd.DataFrame, y: np.ndarray
) -> Tuple[LogisticRegression, LogisticRegression, np.ndarray, np.ndarray]:
    """
    Fit a baseline and a simple "mitigated" logistic regression model.

    Mitigation here is intentionally simple: we use class weights to reduce
    disparity between positive and negative classes, illustrating how ERH
    can be used to compare before/after interventions.
    """
    if LogisticRegression is None or train_test_split is None or StandardScaler is None:
        raise ImportError(
            "scikit-learn is required for the real-data case study. "
            "Install scikit-learn>=1.0.0 to run this script."
        )

    x_train, x_test, y_train, y_test = train_test_split(
        X.values, y, test_size=0.3, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    # Baseline model (no explicit class weighting)
    base = LogisticRegression(max_iter=1000, n_jobs=None)
    base.fit(x_train_scaled, y_train)
    base_probs = base.predict_proba(x_test_scaled)[:, 1]
    base_preds = (base_probs >= 0.5).astype(int)

    # Simple mitigation: use balanced class weights
    mitigated = LogisticRegression(max_iter=1000, class_weight="balanced", n_jobs=None)
    mitigated.fit(x_train_scaled, y_train)
    mit_probs = mitigated.predict_proba(x_test_scaled)[:, 1]
    mit_preds = (mit_probs >= 0.5).astype(int)

    return base, mitigated, base_preds - y_test, mit_preds - y_test


def compute_complexity_from_scores(
    X: pd.DataFrame, probs: np.ndarray
) -> np.ndarray:
    """
    Define a simple complexity proxy for each test point.

    We combine:
    - Feature magnitude (L2 norm of standardized features)
    - Predictive uncertainty (higher when probability is near 0.5)

    and map the result monotonically into an integer scale [1, 100].
    """
    # Use feature magnitude as a proxy for ``information load''
    feature_mag = np.linalg.norm(X.values, axis=1)
    feature_mag = (feature_mag - feature_mag.min()) / (feature_mag.max() - feature_mag.min() + 1e-8)

    # Predictive uncertainty: highest near 0.5
    uncertainty = 1.0 - np.abs(probs - 0.5) * 2.0  # in [0,1]

    raw = 0.5 * feature_mag + 0.5 * uncertainty
    # Monotone map to [1, 100]
    scaled = 1 + 99 * (raw - raw.min()) / (raw.max() - raw.min() + 1e-8)
    return scaled.astype(int)


def compute_erh_curves(
    errors: np.ndarray,
    complexities: np.ndarray,
    x_max: int = 100,
) -> Dict[str, np.ndarray]:
    """
    Compute empirical Pi(x), a simple baseline B(x), and E(x) for a set of
    signed errors and complexity scores.

    For this case study we treat any misclassification as a ``prime-level''
    event and count all misclassified points as ethical primes. This is a
    simplification relative to the full importance-weighted definition, but
    suffices to illustrate ERH-style growth analysis on real data.
    """
    misclassified = (errors != 0).astype(int)
    x_vals = np.arange(1, x_max + 1)

    pi_x = []
    for x in x_vals:
        mask = complexities <= x
        pi_x.append(int(misclassified[mask].sum()))
    pi_x = np.array(pi_x, dtype=float)

    # Simple baseline: scaled x / log(1+x) with scale chosen so that B(x_max) = Pi(x_max)
    with np.errstate(divide="ignore", invalid="ignore"):
        baseline_shape = x_vals / np.log1p(x_vals)
        if baseline_shape[-1] <= 0:
            baseline_shape[-1] = 1.0
        scale = pi_x[-1] / baseline_shape[-1] if baseline_shape[-1] > 0 else 1.0
        b_x = scale * baseline_shape

    e_x = pi_x - b_x

    return {
        "x": x_vals,
        "Pi": pi_x,
        "B": b_x,
        "E": e_x,
    }


def run_adult_erh_analysis(data_path: Path | None = None) -> Dict[str, Any]:
    """
    Run ERH-style analysis on Adult Income: returns x, E_x, alpha, C.
    Mirrors COMPAS logic for consistency in empirical validation.
    """
    path = (data_path or DEFAULT_DATA_PATH).resolve()
    if not path.exists():
        return {"error": "Adult CSV not found"}
    if LogisticRegression is None or train_test_split is None or StandardScaler is None:
        return {"error": "scikit-learn required"}
    try:
        df = load_adult_dataset(path)
        X, y, _ = preprocess_adult(df)
        x_train, x_test, y_train, y_test = train_test_split(
            X.values, y, test_size=0.3, random_state=42, stratify=y
        )
        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train)
        x_test_scaled = scaler.transform(x_test)
        base = LogisticRegression(max_iter=1000, n_jobs=None)
        base.fit(x_train_scaled, y_train)
        base_probs = base.predict_proba(x_test_scaled)[:, 1]
        base_preds = (base_probs >= 0.5).astype(int)
        base_err = (base_preds - y_test).astype(float)
        base_complexities = compute_complexity_from_scores(
            pd.DataFrame(x_test_scaled), base_probs
        )
        curves = compute_erh_curves(base_err, base_complexities, x_max=100)
        x = np.array(curves["x"])
        E_x = np.array(curves["E"])
        alpha, C = _fit_power_law_adult(x, np.abs(E_x))
        return {"x": x.tolist(), "E_x": E_x.tolist(), "alpha": alpha, "C": C}
    except Exception as e:
        return {"error": str(e)}


def _fit_power_law_adult(x: np.ndarray, abs_E: np.ndarray, x_min: int = 10) -> Tuple[float, float]:
    """Fit |E(x)| ~ C x^alpha for Adult data."""
    try:
        from scipy.optimize import curve_fit
    except ImportError:
        mask = (x >= x_min) & (abs_E > 1e-12)
        if mask.sum() < 2:
            return 0.0, 1.0
        log_x = np.log(x[mask])
        log_e = np.log(abs_E[mask] + 1e-8)
        coeffs = np.polyfit(log_x, log_e, 1)
        return float(coeffs[0]), float(np.exp(coeffs[1]))

    def _power(x_arr: np.ndarray, c: float, a: float) -> np.ndarray:
        return c * np.power(x_arr, a)

    mask = (x >= x_min) & (abs_E > 1e-12)
    if mask.sum() < 2:
        return 0.0, 1.0
    try:
        popt, _ = curve_fit(_power, x[mask], abs_E[mask] + 1e-8, p0=[1.0, 0.5], maxfev=5000)
        return float(popt[1]), float(popt[0])
    except Exception:
        return 0.0, 1.0


def compute_real_world_alpha(
    data_path: Path | None = None,
) -> float | None:
    """
    Compute baseline alpha for Adult Income dataset (real-world error growth).

    Returns None if dataset or scikit-learn unavailable.
    Used by alpha comparison scripts.
    """
    if LogisticRegression is None or train_test_split is None or StandardScaler is None:
        return None
    path = (data_path or DEFAULT_DATA_PATH).resolve()
    if not path.exists():
        return None
    try:
        df = load_adult_dataset(path)
        X, y, _ = preprocess_adult(df)
        x_train, x_test, y_train, y_test = train_test_split(
            X.values, y, test_size=0.3, random_state=42, stratify=y
        )
        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train)
        x_test_scaled = scaler.transform(x_test)
        base = LogisticRegression(max_iter=1000, n_jobs=None)
        base.fit(x_train_scaled, y_train)
        base_probs = base.predict_proba(x_test_scaled)[:, 1]
        base_preds = (base_probs >= 0.5).astype(int)
        base_err = base_preds - y_test
        base_complexities = compute_complexity_from_scores(
            pd.DataFrame(x_test), base_probs
        )
        curves = compute_erh_curves(base_err, base_complexities, x_max=100)
        x, e = curves["x"], np.abs(curves["E"])
        mask = x >= 10
        if e[mask].sum() == 0:
            return 0.0
        log_x = np.log(x[mask])
        log_e = np.log(e[mask] + 1e-8)
        return float(np.polyfit(log_x, log_e, 1)[0])
    except Exception:
        return None


def summarize_case_study(
    base_errors: np.ndarray,
    mit_errors: np.ndarray,
    base_complexities: np.ndarray,
    mit_complexities: np.ndarray,
) -> Dict[str, Dict[str, float]]:
    """
    Produce a coarse summary comparing baseline vs mitigated models in terms
    of overall error rate and ERH-style growth.
    """
    def _summary(errors: np.ndarray, complexities: np.ndarray) -> Dict[str, float]:
        mis = (errors != 0).astype(int)
        overall_error = float(mis.mean())

        curves = compute_erh_curves(errors, complexities, x_max=100)
        x = curves["x"]
        e = np.abs(curves["E"])

        # Fit |E(x)| ~ C x^alpha in log-log space for x >= x0
        x0 = 10
        mask = x >= x0
        if e[mask].sum() == 0:
            alpha = 0.0
        else:
            # Add small epsilon to avoid log(0)
            log_x = np.log(x[mask])
            log_e = np.log(e[mask] + 1e-8)
            coeffs = np.polyfit(log_x, log_e, 1)
            alpha = float(coeffs[0])

        return {
            "overall_error_rate": overall_error,
            "estimated_alpha": alpha,
        }

    return {
        "baseline": _summary(base_errors, base_complexities),
        "mitigated": _summary(mit_errors, mit_complexities),
    }


def write_markdown_report(
    output_path: Path,
    stats: Dict[str, Dict[str, float]],
) -> None:
    """
    Write a concise Markdown report summarizing the real-data case study.
    """
    output_path = _safe_resolve_output(output_path)

    lines = []
    lines.append("# Real-Data Case Study: Adult Income and ERH\n")
    lines.append(
        "This report summarizes a small real-data experiment applying the "
        "Ethical Riemann Hypothesis (ERH) framework to the UCI Adult Income dataset.\n"
    )

    lines.append("## Experimental Setup\n")
    lines.append(
        "- **Dataset**: Adult Income (binary classification: income > 50K vs. <= 50K)\n"
        "- **Model family**: Logistic regression\n"
        "- **Baseline model**: Standard logistic regression without class reweighting\n"
        "- **Mitigated model**: Logistic regression with `class_weight='balanced'`\n"
        "- **Complexity proxy**: Combination of feature magnitude and predictive uncertainty\n"
        "- **Ethical primes (simplified)**: All misclassified test points\n"
    )

    lines.append("## Summary Statistics\n")
    for key in ["baseline", "mitigated"]:
        s = stats[key]
        lines.append(f"### {key.capitalize()} model\n")
        lines.append(f"- Overall error rate: {s['overall_error_rate']:.3f}\n")
        lines.append(f"- Estimated ERH growth exponent α: {s['estimated_alpha']:.3f}\n")
        lines.append("")

    lines.append("## Interpretation (Qualitative)\n")
    lines.append(
        "The overall error rate captures conventional predictive performance, "
        "while the ERH growth exponent α reflects how quickly structural "
        "misjudgments accumulate as complexity increases.\n"
    )
    lines.append(
        "- A **smaller α** (more negative or closer to zero from below) indicates "
        "that error growth across complexity levels is well-controlled.\n"
        "- If mitigation reduces overall error **and** lowers α, this suggests "
        "that the intervention not only improves pointwise accuracy but also "
        "stabilizes the structural error landscape.\n"
    )
    lines.append(
        "This case study illustrates how ERH-style analysis can be layered on top "
        "of standard metrics to provide a macro-level view of error growth patterns "
        "in real models."
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run_real_data_case_study(
    data_path: Path | None = None,
    output_markdown: Path | None = None,
) -> None:
    """
    High-level entry point for the Adult Income ERH case study.

    This function is safe to call from CI: if either the dataset or scikit-learn
    is unavailable, it will log a message and exit successfully without writing
    a report.
    """
    data_path = (data_path or DEFAULT_DATA_PATH).resolve()
    output_markdown = output_markdown or DEFAULT_OUTPUT_MD

    if LogisticRegression is None:
        logger.info(
            "[Adult ERH] scikit-learn not installed; skipping real-data case study. "
            "Install scikit-learn>=1.0.0 to enable this experiment."
        )
        return

    if not data_path.exists():
        logger.info(
            "[Adult ERH] Dataset not found at %s; skipping real-data case study. "
            "Place an adult.csv file under data/ to enable this experiment.",
            data_path,
        )
        return

    try:
        df = load_adult_dataset(data_path)
        X, y, _ = preprocess_adult(df)

        # We use the signed error vectors returned by fit_logistic_models;
        # for complexity we rely on feature magnitude only, which is sufficient
        # for illustrating ERH-style growth curves on real data.
        _, _, base_err, mit_err = fit_logistic_models(X, y)

        x_matrix = X.values
        dummy_probs = np.full(shape=(len(x_matrix),), fill_value=0.5)

        base_complexities = compute_complexity_from_scores(
            pd.DataFrame(x_matrix), dummy_probs
        )
        mit_complexities = base_complexities.copy()

        stats = summarize_case_study(
            base_errors=base_err,
            mit_errors=mit_err,
            base_complexities=base_complexities,
            mit_complexities=mit_complexities,
        )

        write_markdown_report(output_markdown, stats)
        logger.info("[Adult ERH] Real-data case study report written to %s", output_markdown)
    except Exception as e:  # pragma: no cover - defensive guard for CI
        logger.error("[Adult ERH] Case study failed with error: %s. Skipping report generation.", e, exc_info=True)


def run_intersectional_erh_analysis(
    df: pd.DataFrame,
    protected_cols: list | None = None,
) -> Dict[str, Any]:
    """Demonstrate IntersectionalJudge on Adult Income data.

    For each combination of protected_cols values the function fits an
    IntersectionalJudge around a BiasedJudge, evaluates ERH on the group's
    actions, and returns the per-group ERHCheckResult.

    Parameters
    ----------
    df : pd.DataFrame
        Preprocessed Adult Income DataFrame.  Must contain the columns listed
        in protected_cols as well as the columns expected by preprocess_adult().
    protected_cols : list of str, optional
        Demographic columns to intersect. Defaults to ["sex", "race"].

    Returns
    -------
    dict
        {"group_label": ERHCheckResult}  for each group with enough data.
        Returns {} if required libraries are unavailable.
    """
    if protected_cols is None:
        protected_cols = ["sex", "race"]

    try:
        from erh_core.core.judgement_system import (
            BiasedJudge, IntersectionalJudge, evaluate_judgement,
        )
        from erh_core.core.action_space import Action
        from erh_core.core.ethical_primes import select_ethical_primes, compute_Pi_and_error
        from erh_core.analysis.erh_checks import check_erh_bound_structured, ERHCheckResult
    except ImportError:
        logger.warning(
            "[Adult ERH] erh_core not available — skipping intersectional analysis."
        )
        return {}

    try:
        X, y, _ = preprocess_adult(df)
    except Exception as exc:
        logger.error("[Adult ERH] preprocess_adult failed: %s", exc, exc_info=True)
        return {}

    # Map rows to Action objects using row index as action id
    # complexity ≈ L1 norm of row features (normalised), V = 2*y - 1 ∈ {-1, 1}
    actions: list[Action] = []
    for i, (idx, row) in enumerate(X.iterrows()):
        c_val = max(1, int(np.linalg.norm(row.values) * 5))
        V = 2.0 * float(y.iloc[i]) - 1.0
        actions.append(Action(id=i, c=c_val, V=V, w=1.0))

    # Attach protected-attribute string to each action via description field
    for i, (idx, _) in enumerate(X.iterrows()):
        parts = []
        for col in protected_cols:
            if col in df.columns:
                parts.append(str(df.loc[idx, col]) if idx in df.index else "unknown")
        actions[i].description = "_".join(parts) if parts else "unknown"

    inner_judge = BiasedJudge(bias_strength=0.15, noise_scale=0.1)
    group_key = lambda a: a.description or "unknown"  # noqa: E731
    judge = IntersectionalJudge(group_key=group_key, inner_judge=inner_judge, name="IntersectionalERH")

    evaluate_judgement(actions, judge, tau=0.3, inplace=True)
    group_metrics = judge.get_group_error_rates(actions)

    results: Dict[str, Any] = {}
    # Group actions by label and compute per-group ERH
    from collections import defaultdict
    grouped: dict = defaultdict(list)
    for a in actions:
        grouped[group_key(a)].append(a)

    for group_label, group_actions in grouped.items():
        if len(group_actions) < 10:
            continue
        primes = select_ethical_primes(group_actions)
        if not primes:
            continue
        x_values, _pi, E_x = compute_Pi_and_error(group_actions, primes)
        if len(x_values) < 2:
            continue
        erh_result = check_erh_bound_structured(E_x, x_values, judge_name=group_label)
        results[group_label] = erh_result
        logger.info(
            "[Adult ERH Intersectional] group=%s n=%d erh_satisfied=%s violation_rate=%.3f",
            group_label, len(group_actions),
            erh_result.erh_satisfied, erh_result.violation_rate,
        )

    return results


if __name__ == "__main__":  # pragma: no cover
    # If the environment variable is set, treat it as a file *name* only,
    # and place the report under the default output directory. This prevents
    # path traversal while still allowing customization.
    env_value = os.environ.get("ERH_REAL_DATA_REPORT")
    if env_value:
        safe_name = Path(env_value).name
        out_path = DEFAULT_OUTPUT_MD.parent / safe_name
    else:
        out_path = DEFAULT_OUTPUT_MD
    run_real_data_case_study(output_markdown=out_path)


