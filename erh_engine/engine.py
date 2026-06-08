"""
Engine adapter: map the generic :class:`Sample` contract onto the canonical
``erh_core`` pipeline and return a normalized :class:`EvaluateResponse`.

Pipeline (all algorithm work delegated to ``erh_core``):

    Sample[]  -> erh_core.Action[]  (V, J, delta, mistake_flag, w, c filled)
              -> select_ethical_primes
              -> compute_Pi_and_error  (Pi(x), B(x), E(x))
              -> check_erh_bound_structured  (ERHCheckResult)
              -> analyze_error_growth  (alpha, r_squared)

This module deliberately contains no ERH math of its own.
"""

from __future__ import annotations

import math
from typing import List

import numpy as np

from erh_core.core.action_space import Action
from erh_core.core.ethical_primes import (
    select_ethical_primes,
    compute_Pi_and_error,
    analyze_error_growth,
)
from erh_core.analysis.erh_checks import check_erh_bound_structured

from .contracts.schemas import (
    EvaluateRequest,
    EvaluateResponse,
    EvaluateParams,
    Curve,
    PrimeRef,
    Sample,
)


def _samples_to_actions(samples: List[Sample], tau: float) -> List[Action]:
    """Build judged ``erh_core`` Actions directly from samples.

    Because samples already carry both V and J, we compute ``delta`` and
    ``mistake_flag`` here rather than running a synthetic judge — this keeps the
    engine domain-agnostic while reusing the exact prime-selection / error
    machinery downstream.
    """
    actions: List[Action] = []
    for idx, s in enumerate(samples):
        delta = float(s.judgment - s.value)
        action = Action(
            id=idx,
            c=int(max(1, round(s.complexity))),
            V=float(s.value),
            w=float(s.weight),
            J=float(s.judgment),
            delta=delta,
            mistake_flag=1 if abs(delta) > tau else 0,
            description=str(s.id),
        )
        actions.append(action)
    return actions


def _finite(value: float, default: float) -> float:
    """Coerce NaN/inf to a JSON-safe default (flat error profiles yield NaN fits)."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def _risk_score(estimated_exponent: float, violation_rate: float, max_ratio: float) -> float:
    """Normalize ERH diagnostics into a 0-100 risk score (higher = unhealthier).

    Combines three signals, each clamped to [0, 1]:
      * exponent drift above the healthy 0.5 line,
      * fraction of complexities breaching the theoretical bound,
      * how far the worst point exceeds the bound.
    """
    exp_term = min(1.0, max(0.0, (estimated_exponent - 0.5) / 0.5)) if math.isfinite(estimated_exponent) else 1.0
    viol_term = min(1.0, max(0.0, violation_rate)) if math.isfinite(violation_rate) else 1.0
    ratio_term = min(1.0, max(0.0, (max_ratio - 1.0))) if math.isfinite(max_ratio) else 1.0
    score = 100.0 * (0.4 * exp_term + 0.35 * viol_term + 0.25 * ratio_term)
    return round(float(score), 2)


def evaluate(request: EvaluateRequest) -> EvaluateResponse:
    """Run the full ERH evaluation for a batch of samples."""
    params: EvaluateParams = request.params
    samples = request.samples

    if not samples:
        return EvaluateResponse(
            erh_satisfied=True,
            risk_score=0.0,
            violation_rate=0.0,
            max_ratio=0.0,
            bound_value=0.0,
            estimated_exponent=0.5,
            r_squared=1.0,
            num_samples=0,
            num_primes=0,
            bound_type="erh_empty",
            judge_name=request.judge_name,
        )

    actions = _samples_to_actions(samples, tau=params.tau)
    context_by_id = {str(s.id): s.context for s in samples}

    primes = select_ethical_primes(
        actions,
        importance_quantile=params.importance_quantile,
        strategy="importance",
    )

    x_max = params.x_max or max(1, max(a.c for a in actions))

    if primes:
        Pi_x, _B_x, E_x, x_vals = compute_Pi_and_error(
            primes, X_max=x_max, baseline=params.baseline
        )
    else:
        # No critical misjudgments => flat, healthy error profile.
        x_vals = np.arange(1, x_max + 1, dtype=float)
        Pi_x = np.zeros_like(x_vals)
        E_x = np.zeros_like(x_vals)

    check = check_erh_bound_structured(
        E_x,
        x_vals,
        C=params.C,
        epsilon=params.epsilon,
        slack_factor=params.slack_factor,
        allowed_violation_rate=params.allowed_violation_rate,
        judge_name=request.judge_name,
    )

    growth = analyze_error_growth(E_x, x_vals)
    estimated_exponent = _finite(growth.get("estimated_exponent", growth.get("alpha", 0.5)), 0.5)
    r_squared = _finite(growth.get("r_squared", 0.0), 0.0)
    violation_rate = _finite(check.violation_rate, 0.0)
    max_ratio = _finite(check.max_ratio, 0.0)
    bound_value = _finite(check.bound_value, 0.0)

    prime_refs = [
        PrimeRef(
            id=str(a.description if a.description is not None else a.id),
            complexity=float(a.c),
            delta=float(a.delta if a.delta is not None else 0.0),
            weight=float(a.w),
            context=context_by_id.get(str(a.description), {}),
        )
        for a in primes
    ]

    response = EvaluateResponse(
        erh_satisfied=bool(check.erh_satisfied),
        risk_score=_risk_score(estimated_exponent, violation_rate, max_ratio),
        violation_rate=violation_rate,
        max_ratio=max_ratio,
        bound_value=bound_value,
        estimated_exponent=estimated_exponent,
        r_squared=r_squared,
        num_samples=len(samples),
        num_primes=len(primes),
        bound_type=check.bound_type,
        judge_name=request.judge_name,
        primes=prime_refs,
    )

    if params.include_curves:
        response.pi_curve = Curve(x=[float(v) for v in x_vals], y=[float(v) for v in Pi_x])
        response.error_curve = Curve(x=[float(v) for v in x_vals], y=[float(v) for v in E_x])

    return response
