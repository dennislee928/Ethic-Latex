"""Thin re-export from erh_core (Single Source of Truth)."""

from erh_core.core.temporal_erh import (
    EthicalDriftMonitor,
    compute_baseline_temporal,
    compute_E_temporal,
    compute_Pi_temporal,
    detect_mule_anomalies,
    simulate_ethical_drift_scenario,
    simulate_mule_effect,
    track_error_evolution,
)

__all__ = [
    "EthicalDriftMonitor",
    "compute_baseline_temporal",
    "compute_E_temporal",
    "compute_Pi_temporal",
    "detect_mule_anomalies",
    "simulate_ethical_drift_scenario",
    "simulate_mule_effect",
    "track_error_evolution",
]
