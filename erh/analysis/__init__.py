"""Analysis modules for zeta functions, spectrum, and statistics."""

from .zeta_function import (
    build_m_sequence,
    ethical_zeta_product,
    find_approximate_zeros,
    compute_spectrum,
)
from .statistics import (
    fit_error_growth,
    compare_judges,
    detect_structural_bias,
    generate_report,
)

# Psychohistory analysis modules
from .temporal_analysis import (
    analyze_temporal_trends,
    detect_anomalies,
    forecast_error_growth,
    compute_temporal_erh_satisfaction,
)
from .opinion_dynamics import (
    degroot_model,
    hegselmann_krause_model,
    aggregate_beliefs,
    compute_group_error,
)
from .fluid_model import (
    solve_error_density_pde,
    fit_fluid_parameters,
    detect_critical_phenomena,
    compute_steady_state,
)

__all__ = [
    "build_m_sequence",
    "ethical_zeta_product",
    "find_approximate_zeros",
    "compute_spectrum",
    "fit_error_growth",
    "compare_judges",
    "detect_structural_bias",
    "generate_report",
    # Psychohistory
    "analyze_temporal_trends",
    "detect_anomalies",
    "forecast_error_growth",
    "compute_temporal_erh_satisfaction",
    "degroot_model",
    "hegselmann_krause_model",
    "aggregate_beliefs",
    "compute_group_error",
    "solve_error_density_pde",
    "fit_fluid_parameters",
    "detect_critical_phenomena",
    "compute_steady_state",
]

