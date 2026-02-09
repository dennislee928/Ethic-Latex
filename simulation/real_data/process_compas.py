"""
Process COMPAS recidivism data for ERH error analysis.

Loads compas-scores-two-years.csv.
Maps two_year_recid (Truth) vs decile_score (Judgment).
Computes E(x) where x is priors_count (complexity proxy).
Outputs compas_error_rates.json for plotting and alpha calculation.

Phase transition analysis: decile 1-4 = low risk, 8-10 = high risk.
Observe error spike in 5-7 (fuzzy zone).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "simulation" / "output" / "compas_error_rates.json"


def process_compas(
    csv_path: Path | None = None,
    output_path: Path | None = None,
) -> Dict[str, Any]:
    """
    Run ERH-style analysis on COMPAS and save to JSON.

    Returns
    -------
    dict
        x, E_x, alpha, C; or error key.
    """
    try:
        from simulation.real_data.compas_case_study import run_compas_erh_analysis

        result = run_compas_erh_analysis(data_path=csv_path)
    except ImportError:
        result = {"error": "compas_case_study not found"}

    out = output_path or DEFAULT_OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result


def run_compas_erh_analysis_for_plot(
    csv_path: Path | None = None,
    output_path: Path | None = None,
) -> Dict[str, Any]:
    """Alias for process_compas."""
    return process_compas(csv_path=csv_path, output_path=output_path)


if __name__ == "__main__":
    r = process_compas()
    if "error" in r:
        print(f"Error: {r['error']}")
    else:
        print(f"COMPAS: α ≈ {r['alpha']:.4f}")
        print(f"Saved to {DEFAULT_OUTPUT}")
