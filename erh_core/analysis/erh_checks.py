"""
ERH Consistency Checks

This module centralizes the operational definition of when a simulated
system “satisfies” the Ethical Riemann Hypothesis (ERH) style bound.

We work with a discrete error profile E(x) defined on integer
complexities x = 1, 2, ..., X_max and test it against the inequality

    |E(x)| ≤ C · x^(1/2 + ε)

for configurable constants C, ε > 0. To make this usable in noisy,
finite-sample simulations, we allow a small slack in two ways:

1. A multiplicative slack factor on the bound (e.g. 1.5 ×),
2. A small allowed fraction of x where the bound can be (slightly)
   violated.

All high-level reporting (CSV, Markdown reports, notebooks) should rely
on this module so that the ERH decision logic stays consistent.
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

import numpy as np

if TYPE_CHECKING:
    from erh_core.core.judgement_system import BaseJudge
    from erh_core.core.action_space import Action

logger = logging.getLogger(__name__)


@dataclass
class ERHCheckResult:
    """Structured result from an ERH bound check.

    Replaces the anonymous dict previously returned by check_erh_bound(),
    adding confidence_level, bound_value, bound_type, and an optional
    judge_name so callers always know the full provenance of the result.
    """

    erh_satisfied: bool
    violation_rate: float
    bound_value: float       # max C·x^(0.5+ε) across all valid x
    max_ratio: float         # max |E(x)| / (C·x^(0.5+ε))
    num_points: int
    confidence_level: float  # 1.0 - allowed_violation_rate
    sample_size: int         # semantic alias for num_points
    bound_type: str          # e.g. “erh_slack_1.5” or “erh_strict”
    C: float
    epsilon: float
    slack_factor: float
    judge_name: Optional[str] = None


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
    # ENH-008: Explicit parameter validation — raise on invalid inputs rather
    # than silently returning NaN or incorrect results.
    if E_x is None or x_values is None:
        raise ValueError("E_x and x_values must not be None.")

    E_x = np.asarray(E_x, dtype=float)
    x_values = np.asarray(x_values, dtype=float)

    if E_x.shape != x_values.shape:
        raise ValueError(
            f"Shape mismatch: E_x has shape {E_x.shape} but x_values has shape {x_values.shape}."
        )
    if C <= 0:
        raise ValueError(f"C must be positive, got C={C}.")
    if epsilon < 0:
        raise ValueError(f"epsilon must be non-negative, got epsilon={epsilon}.")
    if not (0.0 <= allowed_violation_rate <= 1.0):
        raise ValueError(
            f"allowed_violation_rate must be in [0, 1], got {allowed_violation_rate}."
        )
    if slack_factor <= 0:
        raise ValueError(f"slack_factor must be positive, got slack_factor={slack_factor}.")

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
    # Avoid division by zero, though x>0 already enforced
    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = np.where(erh_bound > 0, abs_E / erh_bound, np.inf)

    max_ratio = float(np.nanmax(ratios))

    # Strict violations of the theoretical bound (ratio > 1)
    violation_mask = ratios > 1.0
    num_points = int(valid_mask.sum())
    violation_rate = float(np.mean(violation_mask)) if num_points > 0 else float("nan")

    # Global ERH decision:
    #  - Most points must respect the theoretical bound (violation rate small),
    #  - No point should exceed the slacked practical bound.
    exceeds_slack = max_ratio > slack_factor
    erh_satisfied = (violation_rate <= allowed_violation_rate) and (not exceeds_slack)

    return {
        "erh_satisfied": erh_satisfied,
        "max_ratio": max_ratio,
        "violation_rate": violation_rate,
        "num_points": num_points,
    }


def check_erh_bound_structured(
    E_x: np.ndarray,
    x_values: np.ndarray,
    C: float = 1.0,
    epsilon: float = 0.1,
    slack_factor: float = 1.5,
    allowed_violation_rate: float = 0.05,
    judge_name: Optional[str] = None,
) -> ERHCheckResult:
    """Typed wrapper around check_erh_bound() returning an ERHCheckResult.

    The existing check_erh_bound() signature and return type are untouched;
    this function wraps it for callers that want a structured result object
    with provenance metadata (confidence_level, bound_type, judge_name, etc.).

    Parameters
    ----------
    E_x, x_values, C, epsilon, slack_factor, allowed_violation_rate :
        Same as check_erh_bound().
    judge_name : str, optional
        Name of the judge that produced E_x, stored in the result for
        traceability.

    Returns
    -------
    ERHCheckResult
    """
    raw = check_erh_bound(
        E_x, x_values,
        C=C, epsilon=epsilon,
        slack_factor=slack_factor,
        allowed_violation_rate=allowed_violation_rate,
    )

    # Compute max theoretical bound across valid x for the bound_value field
    x_arr = np.asarray(x_values, dtype=float)
    valid = x_arr[x_arr > 0]
    bound_value = float(np.max(C * (valid ** (0.5 + epsilon)))) if len(valid) else float("nan")

    num_pts = raw["num_points"]
    bound_type = f"erh_slack_{slack_factor}" if slack_factor != 1.0 else "erh_strict"

    return ERHCheckResult(
        erh_satisfied=bool(raw["erh_satisfied"]),
        violation_rate=float(raw["violation_rate"]),
        bound_value=bound_value,
        max_ratio=float(raw["max_ratio"]),
        num_points=num_pts,
        confidence_level=1.0 - allowed_violation_rate,
        sample_size=num_pts,
        bound_type=bound_type,
        C=C,
        epsilon=epsilon,
        slack_factor=slack_factor,
        judge_name=judge_name,
    )


def judge_and_check_erh(
    actions: "List[Action]",
    judge: "BaseJudge",
    E_x: np.ndarray,
    x_values: np.ndarray,
    tau: float = 0.3,
    C: float = 1.0,
    epsilon: float = 0.1,
    slack_factor: float = 1.5,
    allowed_violation_rate: float = 0.05,
    log: bool = True,
) -> ERHCheckResult:
    """Run a judge over actions, then immediately check the ERH bound.

    This is the canonical integration point between the judge layer and the
    ERH analysis layer.  It calls evaluate_judgement() to populate J/delta/
    mistake_flag on each action, then calls check_erh_bound_structured() on
    the provided E_x/x_values arrays (which should have been derived from the
    same judged action set via compute_Pi_and_error()).

    Parameters
    ----------
    actions : List[Action]
        Actions to evaluate (modified in place).
    judge : BaseJudge
        The judge to use.
    E_x : np.ndarray
        Error profile derived from the judged action set.
    x_values : np.ndarray
        Corresponding complexity values.
    tau : float
        Mistake threshold for evaluate_judgement().
    C, epsilon, slack_factor, allowed_violation_rate :
        Forwarded to check_erh_bound_structured().
    log : bool, default=True
        Emit a logger.info line with the ERH verdict.

    Returns
    -------
    ERHCheckResult
        Populated with judge_name from judge.name.
    """
    # Inline import to avoid circular dependency at module load time
    from erh_core.core.judgement_system import evaluate_judgement

    evaluate_judgement(actions, judge, tau=tau, inplace=True)

    result = check_erh_bound_structured(
        E_x, x_values,
        C=C, epsilon=epsilon,
        slack_factor=slack_factor,
        allowed_violation_rate=allowed_violation_rate,
        judge_name=judge.name,
    )

    if log:
        verdict = "SATISFIED" if result.erh_satisfied else "VIOLATED"
        logger.info(
            "ERH bound %s | judge=%s violation_rate=%.3f max_ratio=%.3f n=%d",
            verdict, judge.name, result.violation_rate, result.max_ratio, result.num_points,
        )

    return result

