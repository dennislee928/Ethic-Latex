"""
ERH Consistency Checks (SDK version)

This module mirrors the logic in `simulation.analysis.erh_checks` and
centralizes the operational definition of when an ERH-style bound is
considered satisfied inside the `erh` package.
"""

from typing import Dict

import numpy as np


def check_erh_bound(
    E_x: np.ndarray,
    x_values: np.ndarray,
    C: float = 1.0,
    epsilon: float = 0.1,
    slack_factor: float = 1.5,
    allowed_violation_rate: float = 0.05,
) -> Dict[str, float]:
    """
    Check whether a given error profile E(x) satisfies the ERH-style bound.

    Parameters
    ----------
    E_x : np.ndarray
        Error values E(x) on a 1D grid of complexities.
    x_values : np.ndarray
        Corresponding complexity values x (same shape as E_x).
    C : float, default=1.0
        ERH constant in the theoretical bound |E(x)| ≤ C x^(1/2 + ε).
    epsilon : float, default=0.1
        Small positive epsilon in the exponent (1/2 + ε).
    slack_factor : float, default=1.5
        Practical slack multiplier on the theoretical bound. We treat
        |E(x)| ≤ slack_factor · C x^(1/2 + ε) as acceptable in finite
        data, and report how often the *stricter* theoretical bound is
        crossed.
    allowed_violation_rate : float, default=0.05
        Maximum allowed fraction of x-values where |E(x)| exceeds the
        theoretical bound C x^(1/2 + ε). This lets us treat rare,
        isolated spikes as noise rather than structural ERH failures.

    Returns
    -------
    dict
        Dictionary with:
        - 'erh_satisfied': bool
        - 'max_ratio': max_x |E(x)| / (C x^(1/2 + ε))
        - 'violation_rate': fraction of x with |E(x)| > C x^(1/2 + ε)
        - 'num_points': number of valid (x, E(x)) pairs considered
    """
    if E_x is None or x_values is None:
        return {
            "erh_satisfied": False,
            "max_ratio": float("nan"),
            "violation_rate": float("nan"),
            "num_points": 0,
        }

    E_x = np.asarray(E_x, dtype=float)
    x_values = np.asarray(x_values, dtype=float)

    # Only consider positive complexities and finite errors
    valid_mask = (x_values > 0) & np.isfinite(E_x) & np.isfinite(x_values)
    if not np.any(valid_mask):
        return {
            "erh_satisfied": False,
            "max_ratio": float("nan"),
            "violation_rate": float("nan"),
            "num_points": 0,
        }

    x = x_values[valid_mask]
    abs_E = np.abs(E_x[valid_mask])

    # Theoretical ERH bound and ratios
    erh_bound = C * (x ** (0.5 + epsilon))
    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = np.where(erh_bound > 0, abs_E / erh_bound, np.inf)

    max_ratio = float(np.nanmax(ratios))

    # Strict violations of the theoretical bound (ratio > 1)
    violation_mask = ratios > 1.0
    num_points = int(valid_mask.sum())
    violation_rate = float(np.mean(violation_mask)) if num_points > 0 else float("nan")

    exceeds_slack = max_ratio > slack_factor
    erh_satisfied = (violation_rate <= allowed_violation_rate) and (not exceeds_slack)

    return {
        "erh_satisfied": erh_satisfied,
        "max_ratio": max_ratio,
        "violation_rate": violation_rate,
        "num_points": num_points,
    }


