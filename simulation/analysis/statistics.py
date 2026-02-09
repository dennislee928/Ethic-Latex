"""
Re-export statistics from shared core for simulation.analysis.

Allows 'from simulation.analysis.statistics import compare_judges' etc.
to work; implementation lives in erh_core.analysis.statistics.
"""

from erh_core.analysis.statistics import (
    fit_error_growth,
    fit_power_law_to_data,
    compare_judges,
    detect_structural_bias,
    generate_report,
    calculate_evs,
    calculate_von_neumann_entropy,
    compute_dual_metrics,
    analyze_conservative_judge_anomaly,
)

__all__ = [
    "fit_error_growth",
    "fit_power_law_to_data",
    "compare_judges",
    "detect_structural_bias",
    "generate_report",
    "calculate_evs",
    "calculate_von_neumann_entropy",
    "compute_dual_metrics",
    "analyze_conservative_judge_anomaly",
]
