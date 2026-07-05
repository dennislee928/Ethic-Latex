"""Translation between protobuf messages and Pydantic contract models.

Keeps the gRPC surface a thin transport: it converts to the same
:class:`EvaluateRequest` / :class:`EvaluateResponse` used by REST, so both
paths return identical results.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from ..contracts.schemas import (
    Curve,
    EvaluateParams,
    EvaluateRequest,
    EvaluateResponse,
    PrimeRef,
    Sample,
)
from . import erh_engine_pb2 as pb


def _loads(s: str) -> Dict[str, Any]:
    if not s:
        return {}
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return {}


def request_from_pb(req: "pb.EvaluateRequest") -> EvaluateRequest:
    samples = [
        Sample(
            id=s.id,
            complexity=s.complexity,
            value=s.value,
            judgment=s.judgment,
            weight=s.weight or 1.0,
            context=_loads(s.context_json),
        )
        for s in req.samples
    ]
    p = req.params

    def opt(name: str, default: float) -> float:
        # proto3 `optional` presence: honor an explicit 0, fall back only when unset.
        return getattr(p, name) if p.HasField(name) else default

    params = EvaluateParams(
        tau=opt("tau", 0.3),
        C=opt("C", 1.0),
        epsilon=opt("epsilon", 0.1),
        slack_factor=opt("slack_factor", 1.5),
        allowed_violation_rate=opt("allowed_violation_rate", 0.05),
        baseline=p.baseline or "prime_theorem",
        importance_quantile=opt("importance_quantile", 0.9),
        x_max=p.x_max or None,
        include_curves=p.include_curves,
    )
    return EvaluateRequest(samples=samples, params=params, judge_name=req.judge_name or None)


def response_to_pb(resp: EvaluateResponse) -> "pb.EvaluateResponse":
    out = pb.EvaluateResponse(
        erh_satisfied=resp.erh_satisfied,
        risk_score=resp.risk_score,
        violation_rate=resp.violation_rate,
        max_ratio=resp.max_ratio,
        bound_value=resp.bound_value,
        estimated_exponent=resp.estimated_exponent,
        r_squared=resp.r_squared,
        num_samples=resp.num_samples,
        num_primes=resp.num_primes,
        bound_type=resp.bound_type,
        judge_name=resp.judge_name or "",
    )
    for pr in resp.primes:
        out.primes.append(
            pb.PrimeRef(
                id=pr.id,
                complexity=pr.complexity,
                delta=pr.delta,
                weight=pr.weight,
                context_json=json.dumps(pr.context),
            )
        )
    if resp.pi_curve is not None:
        out.pi_curve.CopyFrom(pb.Curve(x=resp.pi_curve.x, y=resp.pi_curve.y))
    if resp.error_curve is not None:
        out.error_curve.CopyFrom(pb.Curve(x=resp.error_curve.x, y=resp.error_curve.y))
    return out
