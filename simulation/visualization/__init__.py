"""Visualization modules for paper-quality and interactive plots."""

from .plots import (
    plot_Pi_B_E,
    plot_error_growth,
    plot_spectrum,
    plot_zero_distribution,
    plot_judge_comparison,
    setup_paper_style,
)

# Psychohistory visualization modules
from .temporal_plots import (
    plot_3d_error_surface,
    plot_temporal_evolution_animated,
    plot_anomaly_timeline,
    plot_temporal_trends_comparison,
    plot_forecast_comparison,
)
from .network_plots import (
    plot_network_topology,
    plot_opinion_propagation_animated,
    plot_error_density_on_network,
    plot_network_communities,
    plot_centrality_comparison,
)

__all__ = [
    "plot_Pi_B_E",
    "plot_error_growth",
    "plot_spectrum",
    "plot_zero_distribution",
    "plot_judge_comparison",
    "setup_paper_style",
    # Psychohistory
    "plot_3d_error_surface",
    "plot_temporal_evolution_animated",
    "plot_anomaly_timeline",
    "plot_temporal_trends_comparison",
    "plot_forecast_comparison",
    "plot_network_topology",
    "plot_opinion_propagation_animated",
    "plot_error_density_on_network",
    "plot_network_communities",
    "plot_centrality_comparison",
]

