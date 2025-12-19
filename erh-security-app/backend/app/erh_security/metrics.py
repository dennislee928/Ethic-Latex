from __future__ import annotations

from typing import Callable, Dict, List, Tuple

from .mapping import ErhSample

try:  # pragma: no cover - import wiring, behaviour tested via injected callables
    from simulation.core.ethical_primes import (
        select_ethical_primes,
        compute_Pi_and_error,
        analyze_error_growth,
    )
except Exception:  # noqa: BLE001
    # In pure-backend environments the simulation package may not be installed.
    select_ethical_primes = None  # type: ignore[assignment]
    compute_Pi_and_error = None  # type: ignore[assignment]
    analyze_error_growth = None  # type: ignore[assignment]


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
    they use the implementations imported from `simulation.core.ethical_primes`.
    """
    if select_primals is None:
        if select_ethical_primes is None:
            raise RuntimeError("simulation.core.ethical_primes is not available")
        select_primals = select_ethical_primes

    if pi_and_error_fn is None:
        if compute_Pi_and_error is None:
            raise RuntimeError("simulation.core.ethical_primes is not available")
        pi_and_error_fn = compute_Pi_and_error

    if error_growth_fn is None:
        if analyze_error_growth is None:
            raise RuntimeError("simulation.core.ethical_primes is not available")
        error_growth_fn = analyze_error_growth

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




