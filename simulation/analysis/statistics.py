"""
Re-export statistics from shared core for simulation.analysis.

Allows 'from simulation.analysis.statistics import compare_judges' etc.
to work; implementation lives in erh_core.analysis.statistics.
"""

from erh_core.analysis.statistics import (
    fit_error_growth,
    compare_judges,
    detect_structural_bias,
    generate_report,
)

__all__ = [
    "fit_error_growth",
    "compare_judges",
    "detect_structural_bias",
    "generate_report",
]
