"""
Re-export statistics from shared core for erh.analysis.

Allows 'from erh.analysis.statistics import compare_judges' etc.
Implementation lives in erh_core.analysis.statistics.
"""

from erh_core.analysis.statistics import (
    fit_error_growth,
    compare_judges,
    detect_structural_bias,
    generate_report,
    calculate_evs,
)

__all__ = [
    "fit_error_growth",
    "compare_judges",
    "detect_structural_bias",
    "generate_report",
    "calculate_evs",
]
