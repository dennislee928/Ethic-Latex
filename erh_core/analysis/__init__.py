"""
Analysis modules for Ethical Riemann Hypothesis.

This package contains analysis tools including:
- ERH bound checking
- Statistical analysis
- Zeta function analysis
- Baseline comparisons
- Temporal analysis
"""

# Import all analysis modules for easy access
# Use try/except to handle missing or differently named functions
try:
    from erh_core.analysis.erh_checks import (
        check_erh_bound,
        check_erh_bound_structured,
        judge_and_check_erh,
        ERHCheckResult,
    )
except ImportError:
    from .erh_checks import (
        check_erh_bound,
        check_erh_bound_structured,
        judge_and_check_erh,
        ERHCheckResult,
    )

try:
    from erh_core.analysis.statistics import generate_report, bootstrap_exponent_ci
except ImportError:
    from .statistics import generate_report, bootstrap_exponent_ci

try:
    from erh_core.analysis.baseline_comparison import generate_baseline_comparison_report
except ImportError:
    from .baseline_comparison import generate_baseline_comparison_report

try:
    from erh_core.analysis.zeta_function import (
        build_m_sequence, ethical_zeta_product, find_approximate_zeros, compute_spectrum
    )
except ImportError:
    from .zeta_function import (
        build_m_sequence, ethical_zeta_product, find_approximate_zeros, compute_spectrum
    )

# zeta_zeros_analysis may have different function names
try:
    from erh_core.analysis.zeta_zeros_analysis import *
except ImportError:
    try:
        from .zeta_zeros_analysis import *
    except ImportError:
        pass

try:
    from erh_core.analysis.temporal_analysis import (
        analyze_temporal_trends, detect_anomalies, forecast_error_growth
    )
except ImportError:
    from .temporal_analysis import (
        analyze_temporal_trends, detect_anomalies, forecast_error_growth
    )

try:
    from erh_core.analysis.fluid_model import (
        solve_error_density_pde, fit_fluid_parameters, detect_critical_phenomena
    )
except ImportError:
    from .fluid_model import (
        solve_error_density_pde, fit_fluid_parameters, detect_critical_phenomena
    )

try:
    from erh_core.analysis.opinion_dynamics import (
        degroot_model, hegselmann_krause_model, aggregate_beliefs
    )
except ImportError:
    from .opinion_dynamics import (
        degroot_model, hegselmann_krause_model, aggregate_beliefs
    )

try:
    from erh_core.analysis.edge_cases import analyze_edge_cases
except ImportError:
    from .edge_cases import analyze_edge_cases

__all__ = [
    "check_erh_bound",
    "check_erh_bound_structured",
    "judge_and_check_erh",
    "ERHCheckResult",
    "generate_report", "bootstrap_exponent_ci",
    "generate_baseline_comparison_report",
    "build_m_sequence", "ethical_zeta_product", "find_approximate_zeros", "compute_spectrum",
    "analyze_temporal_trends", "detect_anomalies", "forecast_error_growth",
    "solve_error_density_pde", "fit_fluid_parameters", "detect_critical_phenomena",
    "degroot_model", "hegselmann_krause_model", "aggregate_beliefs",
    "analyze_edge_cases",
]

