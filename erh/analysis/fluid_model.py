"""Re-export fluid model from shared core for fallback when erh_core.analysis fails to load."""

from erh_core.analysis.fluid_model import (
    solve_error_density_pde,
    fit_fluid_parameters,
    detect_critical_phenomena,
    compute_steady_state,
)

__all__ = [
    "solve_error_density_pde",
    "fit_fluid_parameters",
    "detect_critical_phenomena",
    "compute_steady_state",
]
