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

__all__ = [
    "build_m_sequence",
    "ethical_zeta_product",
    "find_approximate_zeros",
    "compute_spectrum",
    "fit_error_growth",
    "compare_judges",
    "detect_structural_bias",
    "generate_report",
]

