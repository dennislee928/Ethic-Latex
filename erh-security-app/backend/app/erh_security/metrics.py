from __future__ import annotations

import math
from typing import Callable, Dict, List, Tuple

from .mapping import ErhSample


def compute_delta(sample: ErhSample) -> float:
    """
    Delta between judgment and ground truth: J(a) - V(a).
    """
    return float(sample.judgment_value - sample.ground_truth_value)


def is_mistake(sample: ErhSample, tau: float = 0.0) -> bool:
    """
    A mistake occurs when J(a) and V(a) disagree in sign by at least tau.
    """
    delta = compute_delta(sample)
    if abs(delta) <= tau:
        return False
    return (sample.judgment_value >= 0.0 and sample.ground_truth_value < 0.0) or (
        sample.judgment_value <= 0.0 and sample.ground_truth_value > 0.0
    )


def to_ethical_prime_input(samples: List[ErhSample], tau: float = 0.0) -> List[Tuple[float, float, float, bool]]:
    """
    Convert ErhSample list into the basic tuples consumed by ethical_primes helpers.

    Each tuple is (complexity, weight, delta, is_mistake).
    """
    data: List[Tuple[float, float, float, bool]] = []
    for s in samples:
        d = compute_delta(s)
        m = is_mistake(s, tau=tau)
        data.append((s.complexity, s.weight, d, m))
    return data


def default_select_ethical_primes(
    data: List[Tuple[float, float, float, bool]],
) -> List[Tuple[float, float, float, bool]]:
    """
    Pick the highest-weight mistakes as "ethical primes".
    """
    mistakes = [row for row in data if row[3]]
    if not mistakes:
        return []

    mistakes.sort(key=lambda row: (row[1], abs(row[2]), row[0]), reverse=True)
    cutoff = max(1, math.ceil(len(mistakes) * 0.1))
    return mistakes[:cutoff]


def default_compute_pi_and_error(
    primes: List[Tuple[float, float, float, bool]],
) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    """
    Build Π(x) and E(x) curves over the observed complexity range.
    """
    if not primes:
      return [], []

    x_max = max(1, math.ceil(max(row[0] for row in primes)))
    total_primes = len(primes)
    density = total_primes / float(x_max)

    pi_curve: List[Tuple[float, float]] = []
    error_curve: List[Tuple[float, float]] = []

    for x in range(1, x_max + 1):
        pi_x = sum(1 for complexity, *_ in primes if complexity <= x)
        baseline = density * x
        pi_curve.append((float(x), float(pi_x)))
        error_curve.append((float(x), float(pi_x - baseline)))

    return pi_curve, error_curve


def default_analyze_error_growth(
    error_curve: List[Tuple[float, float]],
) -> Dict[str, float]:
    """
    Estimate log-log growth of |E(x)| ~ x^alpha using a simple least-squares fit.
    """
    points = [(x, abs(y)) for x, y in error_curve if x > 0 and abs(y) > 0]
    if len(points) < 2:
        return {"alpha": 0.0, "r_squared": 1.0}

    log_x = [math.log(x) for x, _ in points]
    log_y = [math.log(y) for _, y in points]
    mean_x = sum(log_x) / len(log_x)
    mean_y = sum(log_y) / len(log_y)

    ss_xx = sum((x - mean_x) ** 2 for x in log_x)
    if ss_xx == 0:
        return {"alpha": 0.0, "r_squared": 1.0}

    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_x, log_y))
    alpha = ss_xy / ss_xx
    intercept = mean_y - alpha * mean_x

    fitted = [alpha * x + intercept for x in log_x]
    ss_res = sum((y - f) ** 2 for y, f in zip(log_y, fitted))
    ss_tot = sum((y - mean_y) ** 2 for y in log_y)
    r_squared = 1.0 if ss_tot == 0 else max(0.0, 1.0 - ss_res / ss_tot)

    return {"alpha": float(alpha), "r_squared": float(r_squared)}


def analyze_erh_structure(
    samples: List[ErhSample],
    *,
    tau: float = 0.0,
    select_primals: Callable | None = None,
    pi_and_error_fn: Callable | None = None,
    error_growth_fn: Callable | None = None,
) -> Dict[str, object]:
    """
    Run the full ERH analysis pipeline on ERH-on-Security samples.

    The three functional dependencies can be injected for tests; by default
    they use lightweight in-repo defaults that operate on ERH tuple data.
    """
    if select_primals is None:
        select_primals = default_select_ethical_primes

    if pi_and_error_fn is None:
        pi_and_error_fn = default_compute_pi_and_error

    if error_growth_fn is None:
        error_growth_fn = default_analyze_error_growth

    base_data = to_ethical_prime_input(samples, tau=tau)

    primes = select_primals(base_data)
    pi_curve, error_curve = pi_and_error_fn(primes)
    growth_analysis = error_growth_fn(error_curve)

    return {
        "num_samples": len(samples),
        "num_primes": len(primes),
        "pi_curve": pi_curve,
        "error_curve": error_curve,
        "growth": growth_analysis,
    }

