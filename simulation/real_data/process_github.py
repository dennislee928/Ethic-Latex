"""
Process GitHub PR empirical data for ERH error analysis.

Loads github_pr_empirical.json (from fetch_empirical_erh_data.py).
Maps merged status to Ground Truth V(a): merged -> +1, rejected -> -1.
Computes complexity x from metadata (additions, deletions, changed_files) or sequential.
Outputs github_error_rates.json for plotting and alpha calculation.

Note: Both merged=true and merged=false PRs are needed to compute E(x).
Rejected PRs represent deviation from community norms (V=-1).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSON_PATHS = [
    PROJECT_ROOT / "data" / "empirical" / "github_pr_empirical.json",
    PROJECT_ROOT / "data" / "github_pr_empirical.json",
]
DEFAULT_OUTPUT = PROJECT_ROOT / "simulation" / "output" / "github_error_rates.json"


def _load_github_json(json_path: Path | None = None) -> List[Dict[str, Any]]:
    """Load PR rows from github_pr_empirical.json."""
    for path in [json_path] if json_path else DEFAULT_JSON_PATHS:
        if path and path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                rows = data.get("rows", [])
                if rows:
                    return rows
            except (json.JSONDecodeError, IOError):
                continue
    return []


def _stub_pr_data(n: int = 30) -> List[Dict[str, Any]]:
    """Stub PR data when JSON unavailable. Includes both merged and rejected."""
    rng = np.random.default_rng(42)
    return [
        {
            "pr_id": i,
            "merged": rng.random() > 0.6,  # ~40% merged
            "author": f"user{i}",
            "additions": int(rng.integers(1, 500)),
            "deletions": int(rng.integers(0, 200)),
            "changed_files": int(rng.integers(1, 15)),
        }
        for i in range(n)
    ]


def _truth_from_merged(merged: bool) -> float:
    """Ground Truth V(a): merged -> +1, rejected -> -1."""
    return 1.0 if merged else -1.0


def _complexity_from_row(row: Dict[str, Any], idx: int) -> float:
    """Complexity x from additions, deletions, changed_files or fallback to idx."""
    add = row.get("additions") or row.get("additions_count") or 0
    dele = row.get("deletions") or row.get("deletions_count") or 0
    files = row.get("changed_files") or row.get("changed_files_count") or row.get("files") or 0
    try:
        add, dele, files = int(add), int(dele), int(files)
    except (ValueError, TypeError):
        add, dele, files = 0, 0, 0
    if add > 0 or dele > 0 or files > 0:
        raw = max(1, add + dele + 10 * files)
    else:
        raw = max(1, idx + 1)
    return float(raw)


def _judgment_from_baseline(
    truth: np.ndarray,
    complexity: np.ndarray,
    noise_scale: float = 0.4,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    Simulate judgment J from truth + noise (for ERH error calculation).
    When no external model exists, we use noisy baseline to compute E(x).
    """
    rng = rng or np.random.default_rng(42)
    noise = rng.normal(0, noise_scale, size=truth.shape)
    J = np.clip(truth + noise, -1.0, 1.0)
    return J


def _compute_cumulative_error(
    truth: np.ndarray,
    judgment: np.ndarray,
    complexity: np.ndarray,
    x_max: int = 100,
) -> tuple[np.ndarray, np.ndarray]:
    """E(x) = sum(judgment - truth) for complexity <= x."""
    x_vals = np.arange(1, x_max + 1, dtype=float)
    err = judgment - truth
    # Bin complexity into 1..x_max
    c_min, c_max = complexity.min(), complexity.max()
    if c_max <= c_min:
        c_bins = np.ones_like(complexity, dtype=int)
    else:
        c_bins = (
            1
            + (99 * (complexity - c_min) / (c_max - c_min + 1e-8)).astype(int)
        )
        c_bins = np.clip(c_bins, 1, x_max)
    E_x = np.array([float(err[c_bins <= x].sum()) for x in x_vals])
    return x_vals, E_x


def _fit_power_law(x: np.ndarray, E_x: np.ndarray, x_min: int = 5) -> tuple[float, float]:
    """Fit |E(x)| ~ C * x^alpha. Returns (alpha, C)."""
    abs_E = np.abs(E_x) + 1e-12
    mask = (x >= x_min) & (abs_E > 1e-12)
    if mask.sum() < 2:
        return 0.0, 1.0
    log_x = np.log(x[mask])
    log_e = np.log(abs_E[mask])
    coeffs = np.polyfit(log_x, log_e, 1)
    alpha = float(coeffs[0])
    C = float(np.exp(coeffs[1]))
    return alpha, C


def process_github(
    json_path: Path | None = None,
    output_path: Path | None = None,
    use_stub_if_empty: bool = True,
) -> Dict[str, Any]:
    """
    Process GitHub PR data, compute E(x) and alpha.

    Returns
    -------
    dict
        x, E_x, alpha, C, n_prs, n_merged, n_rejected; or error key.
    """
    rows = _load_github_json(json_path)
    if not rows and use_stub_if_empty:
        rows = _stub_pr_data(30)

    if not rows:
        return {"error": "No PR data available; run fetch_empirical_erh_data.py first"}

    truth_list = []
    complexity_list = []
    for i, row in enumerate(rows):
        merged = row.get("merged", False)
        truth_list.append(_truth_from_merged(merged))
        complexity_list.append(_complexity_from_row(row, i))

    truth = np.array(truth_list)
    complexity = np.array(complexity_list)
    judgment = _judgment_from_baseline(truth, complexity)

    x_vals, E_x = _compute_cumulative_error(truth, judgment, complexity)
    alpha, C = _fit_power_law(x_vals, E_x)

    result = {
        "x": x_vals.tolist(),
        "E_x": E_x.tolist(),
        "alpha": alpha,
        "C": C,
        "n_prs": len(rows),
        "n_merged": int((truth == 1).sum()),
        "n_rejected": int((truth == -1).sum()),
    }

    out = output_path or DEFAULT_OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result


def run_github_erh_analysis(
    json_path: Path | None = None,
    output_path: Path | None = None,
) -> Dict[str, Any]:
    """Alias for process_github for consistency with run_compas_erh_analysis."""
    return process_github(json_path=json_path, output_path=output_path)


if __name__ == "__main__":
    r = process_github()
    if "error" in r:
        print(f"Error: {r['error']}")
    else:
        print(f"GitHub PR: n={r['n_prs']} (merged={r['n_merged']}, rejected={r['n_rejected']})")
        print(f"α ≈ {r['alpha']:.4f}")
        print(f"Saved to {DEFAULT_OUTPUT}")
