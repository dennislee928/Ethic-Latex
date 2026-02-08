"""Re-export opinion dynamics from shared core for fallback when erh_core.analysis fails to load."""

from erh_core.analysis.opinion_dynamics import (
    degroot_model,
    hegselmann_krause_model,
    aggregate_beliefs,
    compute_group_error,
)

__all__ = [
    "degroot_model",
    "hegselmann_krause_model",
    "aggregate_beliefs",
    "compute_group_error",
]
