"""Re-export temporal analysis from shared core for fallback when erh_core.analysis fails to load."""

from erh_core.analysis.temporal_analysis import (
    analyze_temporal_trends,
    detect_anomalies,
    forecast_error_growth,
    compute_temporal_erh_satisfaction,
)

__all__ = [
    "analyze_temporal_trends",
    "detect_anomalies",
    "forecast_error_growth",
    "compute_temporal_erh_satisfaction",
]
