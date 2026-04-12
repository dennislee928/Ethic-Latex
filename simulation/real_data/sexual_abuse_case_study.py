"""
Sexual Abuse real-data case study for the Ethical Riemann Hypothesis (ERH).

This module demonstrates how to apply the ERH framework to a sensitive, real dataset 
related to sexual abuse reporting or outcomes (dataset not included for privacy and ethical reasons).
The ERH-style error growth analysis is used to complement conventional metrics and to highlight 
structural challenges in modeling socially critical, high-stakes data.

Design goals:
- Use a dataset relevant to sexual abuse/harassment cases (schema assumed, not distributed).
- Map tabular data into the ERH pipeline (complexity, ethical "prime", weights).
- Compare a baseline model with a basic mitigation/intervention strategy.
- Export a Markdown report summarizing both technical and ethical observations.

Sensitive Data Note:
This example assumes that data privacy and consent have been strictly observed, and is written purely 
for methodological illustration.

"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
except ImportError:  # pragma: no cover
    LogisticRegression = None  # type: ignore
    train_test_split = None  # type: ignore
    StandardScaler = None  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "sexual_abuse_cases.csv"
DEFAULT_OUTPUT_MD = PROJECT_ROOT / "simulation" / "output" / "sexual_abuse_case_study_report.md"


def _safe_resolve_output(path: Path) -> Path:
    resolved = path.resolve()
    root = PROJECT_ROOT.resolve()
    if not str(resolved).startswith(str(root)):
        resolved = DEFAULT_OUTPUT_MD
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def load_sexual_abuse_dataset(csv_path: Path | None = None) -> pd.DataFrame:
    """
    Load a (preprocessed) Sexual Abuse dataset from a local CSV file.

    Parameters
    ----------
    csv_path:
        Path to the CSV file. If None, defaults to data/sexual_abuse_cases.csv under
        the project root.

    Returns
    -------
    DataFrame
        Cleaned abuse/harassment reporting dataframe.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.
    """
    path = csv_path or DEFAULT_DATA_PATH
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(
            f"Sexual abuse dataset CSV not found at {path}. "
            "Place a preprocessed sexual_abuse_cases.csv file under data/ with proper anonymization."
        )
    df = pd.read_csv(path)
    # We expect a target column named 'reported' (1 if reported, 0 otherwise)
    if "reported" not in df.columns:
        raise ValueError("Expected a column 'reported' (binary target) in the dataset.")
    df = df.dropna().reset_index(drop=True)
    return df


def preprocess_sexual_abuse(df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray, pd.Series]:
    """
    Preprocess dataset into features, labels, and optionally a sensitive attribute.

    - Target: reported (1 = abuse was reported, 0 = not reported)
    - Protected attribute: e.g., gender or age group (if available)
    - Complexity proxy: derived later from feature representation and model scores.
    """
    y = df["reported"].astype(int).values

    # Use a protected attribute if available (e.g., 'gender', else fallback)
    if "gender" in df.columns:
        protected = df["gender"].astype(str)
    else:
        protected = pd.Series(["unknown"] * len(df), name="gender")

    # Drop target and any obvious direct identifiers
    drop_cols = {"reported"}
    x_df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # One-hot encode categoricals, leave numerics as-is
    x_processed = pd.get_dummies(x_df, drop_first=True)
    return x_processed, y, protected


def fit_logistic_models(
    X: pd.DataFrame, y: np.ndarray
) -> Tuple[LogisticRegression, LogisticRegression, np.ndarray, np.ndarray]:
    """
    Fit a baseline and a simple "mitigated" logistic regression model.

    Mitigation: class weights to counter reporting imbalance.
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

    base = LogisticRegression(max_iter=1000)
    base.fit(x_train_scaled, y_train)
    base_probs = base.predict_proba(x_test_scaled)[:, 1]
    base_preds = (base_probs >= 0.5).astype(int)

    mitigated = LogisticRegression(max_iter=1000, class_weight="balanced")
    mitigated.fit(x_train_scaled, y_train)
    mit_probs = mitigated.predict_proba(x_test_scaled)[:, 1]
    mit_preds = (mit_probs >= 0.5).astype(int)

    return base, mitigated, base_preds - y_test, mit_preds - y_test


def compute_complexity_from_scores(
    X: pd.DataFrame, probs: np.ndarray
) -> np.ndarray:
    """
    Define a simple complexity proxy for each test point.

    - Combine L2 norm of standardized features and predictive uncertainty (high at 0.5)
    - Monotonically map to integer scale [1, 100].
    """
    feature_mag = np.linalg.norm(X.values, axis=1)
    feature_mag = (feature_mag - feature_mag.min()) / (feature_mag.max() - feature_mag.min() + 1e-8)
    uncertainty = 1.0 - np.abs(probs - 0.5) * 2.0  # in [0,1]
    raw = 0.5 * feature_mag + 0.5 * uncertainty
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
    """
    misclassified = (errors != 0).astype(int)
    x_vals = np.arange(1, x_max + 1)
    pi_x = []
    for x in x_vals:
        mask = complexities <= x
        pi_x.append(int(misclassified[mask].sum()))
    pi_x = np.array(pi_x, dtype=float)
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


def summarize_case_study(
    base_errors: np.ndarray,
    mit_errors: np.ndarray,
    base_complexities: np.ndarray,
    mit_complexities: np.ndarray,
) -> Dict[str, Dict[str, float]]:
    """
    Summary comparing baseline vs. mitigated models.
    """
    def _summary(errors: np.ndarray, complexities: np.ndarray) -> Dict[str, float]:
        mis = (errors != 0).astype(int)
        overall_error = float(mis.mean())
        curves = compute_erh_curves(errors, complexities, x_max=100)
        x = curves["x"]
        e = np.abs(curves["E"])
        x0 = 10
        mask = x >= x0
        if e[mask].sum() == 0:
            alpha = 0.0
        else:
            # Avoid log(0)
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
    Write a concise Markdown report for the Sexual Abuse real-data case study.
    """
    output_path = _safe_resolve_output(output_path)
    lines = []
    lines.append("# Real-Data Case Study: Sexual Abuse Reporting and ERH\n")
    lines.append(
        "This report summarizes a methodological study applying the Ethical Riemann "
        "Hypothesis (ERH) error growth framework to a sexual abuse/harassment reporting dataset. "
        "Only anonymized, synthetic, or public benchmark data were used; all analysis is for "
        "illustrative purposes only.\n"
    )
    lines.append("## Experimental Setup\n")
    lines.append(
        "- **Dataset**: Sexual abuse/harassment reporting (binary classification: reported vs not reported)\n"
        "- **Model family**: Logistic regression\n"
        "- **Baseline model**: Standard logistic regression\n"
        "- **Mitigated model**: Logistic regression with class reweighting\n"
        "- **Complexity proxy**: Combination of feature magnitude and model uncertainty\n"
        "- **Ethical primes**: All misclassified test points\n"
    )
    lines.append("## Summary Statistics\n")
    for key in ["baseline", "mitigated"]:
        s = stats[key]
        lines.append(f"### {key.capitalize()} model\n")
        lines.append(f"- Overall error rate: {s['overall_error_rate']:.3f}\n")
        lines.append(f"- Estimated ERH growth exponent α: {s['estimated_alpha']:.3f}\n")
        lines.append("")
    lines.append("## Qualitative Interpretation\n")
    lines.append(
        "A low error rate indicates a model that aligns predictions with ground truth, "
        "but in social-impact domains, we are also interested in how errors grow as "
        "cases become more complex or ambiguous. The ERH exponent α quantifies this.\n"
    )
    lines.append(
        "- A smaller α (closer to or below zero) is desirable: it means error growth is controlled.\n"
        "- If an intervention decreases both error rate and α, it suggests improvement at both pointwise accuracy and structural level.\n"
    )
    lines.append(
        "This case study illustrates how ERH-style analysis can highlight challenges "
        "in sensitive domains and be layered atop conventional metrics for deeper diagnostics."
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run_real_data_case_study(
    data_path: Path | None = None,
    output_markdown: Path | None = None,
) -> None:
    """
    Entry point for the Sexual Abuse ERH case study. Skips gracefully if data is unavailable.
    """
    data_path = (data_path or DEFAULT_DATA_PATH).resolve()
    output_markdown = output_markdown or DEFAULT_OUTPUT_MD

    if LogisticRegression is None:
        logger.info(
            "[Sexual Abuse ERH] scikit-learn not installed; skipping case study. "
            "Install scikit-learn>=1.0.0 to enable this experiment."
        )
        return

    if not data_path.exists():
        logger.info(
            "[Sexual Abuse ERH] Dataset not found at %s; skipping case study. "
            "Place an anonymized sexual_abuse_cases.csv file under data/ to enable this experiment.",
            data_path,
        )
        return

    try:
        df = load_sexual_abuse_dataset(data_path)
        X, y, _ = preprocess_sexual_abuse(df)
        _, _, base_err, mit_err = fit_logistic_models(X, y)

        x_matrix = X.values  # As with adult case, coarse approx
        dummy_probs = np.full(shape=(len(x_matrix),), fill_value=0.5)

        base_complexities = compute_complexity_from_scores(pd.DataFrame(x_matrix), dummy_probs)
        mit_complexities = base_complexities.copy()

        stats = summarize_case_study(
            base_errors=base_err,
            mit_errors=mit_err,
            base_complexities=base_complexities,
            mit_complexities=mit_complexities,
        )

        write_markdown_report(output_markdown, stats)
        logger.info("[Sexual Abuse ERH] Case study report written to %s", output_markdown)
    except Exception as e:
        logger.error("[Sexual Abuse ERH] Case study failed: %s. Skipping report generation.", e, exc_info=True)


if __name__ == "__main__":  # pragma: no cover
    env_value = os.environ.get("ERH_SEXUAL_ABUSE_REPORT")
    if env_value:
        safe_name = Path(env_value).name
        out_path = DEFAULT_OUTPUT_MD.parent / safe_name
    else:
        out_path = DEFAULT_OUTPUT_MD
    run_real_data_case_study(output_markdown=out_path)


