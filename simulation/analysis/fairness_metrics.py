"""
Fairness and Consistency Metrics

This module provides a small set of standard group-wise fairness and
consistency diagnostics that can be computed on the same simulated
judgment data used for ERH analysis.

The goal is not to be exhaustive, but to offer 1–2 familiar baselines
so that we can compare what ERH-style diagnostics add on top.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np

from ..core.action_space import Action


def compute_group_error_gaps(
    actions: List[Action],
    group_attr: str = "group",
) -> Dict[str, float]:
    """
    Compute simple group-wise error and MAE gaps for a binary (or multi-class)
    sensitive attribute stored on each Action (e.g. action.group).

    Parameters
    ----------
    actions : List[Action]
        Evaluated actions with mistake_flag and delta populated.
    group_attr : str, default='group'
        Name of the attribute on Action that encodes the group label.

    Returns
    -------
    dict
        - 'groups': list of observed group labels
        - 'mistake_rate_by_group': mapping group -> mistake_rate
        - 'mae_by_group': mapping group -> MAE
        - 'max_mistake_gap': max pairwise absolute difference in mistake_rate
        - 'max_mae_gap': max pairwise absolute difference in MAE
    """
    if not actions:
        return {
            "groups": [],
            "mistake_rate_by_group": {},
            "mae_by_group": {},
            "max_mistake_gap": 0.0,
            "max_mae_gap": 0.0,
        }

    # Collect per-group stats
    group_values = {}
    for a in actions:
        group = getattr(a, group_attr, None)
        if group is None:
            continue
        if a.mistake_flag is None or a.delta is None:
            continue
        if group not in group_values:
            group_values[group] = {"mistakes": [], "deltas": []}
        group_values[group]["mistakes"].append(int(a.mistake_flag))
        group_values[group]["deltas"].append(float(a.delta))

    groups = sorted(group_values.keys())
    mistake_rate_by_group = {}
    mae_by_group = {}

    for g in groups:
        data = group_values[g]
        if not data["mistakes"]:
            mistake_rate_by_group[g] = 0.0
            mae_by_group[g] = 0.0
            continue
        mistakes = np.array(data["mistakes"], dtype=float)
        deltas = np.array(data["deltas"], dtype=float)
        mistake_rate_by_group[g] = float(mistakes.mean())
        mae_by_group[g] = float(np.abs(deltas).mean())

    # Compute max pairwise gaps
    max_mistake_gap = 0.0
    max_mae_gap = 0.0
    for i, gi in enumerate(groups):
        for gj in groups[i + 1 :]:
            max_mistake_gap = max(
                max_mistake_gap,
                abs(mistake_rate_by_group[gi] - mistake_rate_by_group[gj]),
            )
            max_mae_gap = max(
                max_mae_gap,
                abs(mae_by_group[gi] - mae_by_group[gj]),
            )

    return {
        "groups": groups,
        "mistake_rate_by_group": mistake_rate_by_group,
        "mae_by_group": mae_by_group,
        "max_mistake_gap": max_mistake_gap,
        "max_mae_gap": max_mae_gap,
    }


def compute_calibration_by_bins(
    actions: List[Action],
    num_bins: int = 10,
    use_complexity: bool = True,
) -> Dict[str, List[float]]:
    """
    Compute a simple calibration / consistency diagnostic by binning either
    complexity c or true value V and comparing bin-wise averages of J and V.

    Parameters
    ----------
    actions : List[Action]
        Evaluated actions with V and J populated.
    num_bins : int, default=10
        Number of bins for the conditioning variable.
    use_complexity : bool, default=True
        If True, bin by complexity c; otherwise bin by true value V.

    Returns
    -------
    dict
        - 'bin_centers': list of bin centers
        - 'mean_true': list of mean V per bin
        - 'mean_pred': list of mean J per bin
        - 'calibration_error': mean |mean_pred - mean_true| over non-empty bins
    """
    if not actions:
        return {
            "bin_centers": [],
            "mean_true": [],
            "mean_pred": [],
            "calibration_error": 0.0,
        }

    if use_complexity:
        xs = np.array([a.c for a in actions], dtype=float)
    else:
        xs = np.array([a.V for a in actions], dtype=float)

    Vs = np.array([a.V for a in actions], dtype=float)
    Js = np.array([a.J for a in actions], dtype=float)

    if len(xs) < 2:
        return {
            "bin_centers": xs.tolist(),
            "mean_true": Vs.tolist(),
            "mean_pred": Js.tolist(),
            "calibration_error": float(np.mean(np.abs(Js - Vs))),
        }

    bins = np.linspace(xs.min(), xs.max(), num_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    mean_true = []
    mean_pred = []
    cal_errors = []

    for i in range(num_bins):
        mask = (xs >= bins[i]) & (xs < bins[i + 1])
        # include right edge in last bin
        if i == num_bins - 1:
            mask = (xs >= bins[i]) & (xs <= bins[i + 1])

        if not np.any(mask):
            mean_true.append(float("nan"))
            mean_pred.append(float("nan"))
            continue

        V_bin = Vs[mask]
        J_bin = Js[mask]
        mt = float(V_bin.mean())
        mp = float(J_bin.mean())
        mean_true.append(mt)
        mean_pred.append(mp)
        cal_errors.append(abs(mp - mt))

    calibration_error = float(np.mean(cal_errors)) if cal_errors else float("nan")

    return {
        "bin_centers": bin_centers.tolist(),
        "mean_true": mean_true,
        "mean_pred": mean_pred,
        "calibration_error": calibration_error,
    }


