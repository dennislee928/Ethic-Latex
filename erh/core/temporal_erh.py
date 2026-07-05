"""Compatibility shim: re-export the canonical temporal_erh from erh_core."""

from erh_core.core.temporal_erh import *  # noqa: F401,F403
from erh_core.core.temporal_erh import (  # noqa: F401
    compute_Pi_temporal,
    compute_E_temporal,
    compute_baseline_temporal,
    track_error_evolution,
    simulate_mule_effect,
    detect_mule_anomalies,
    EthicalDriftMonitor,
    simulate_ethical_drift_scenario,
)
