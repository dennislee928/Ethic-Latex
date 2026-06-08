"""
Canonical ERH evaluation contract.

These Pydantic models are the single source of truth for the request/response
shape used by every surface (REST, gRPC, SDKs, adapters). The gRPC proto in
``erh_engine/proto/erh_engine.proto`` mirrors these fields field-for-field.

A :class:`Sample` is the domain-agnostic unit fed to the engine. Each product
adapter (LLM, IAM, UEBA) is responsible only for turning its raw data into
``Sample`` objects:

* ``complexity`` (x) — how hard / broad the decision is (>= 1).
* ``value`` (V) — the *true* value / least-privilege baseline in [-1, 1].
* ``judgment`` (J) — the system's *actual* decision in [-1, 1].
* ``weight`` (w) — importance / criticality (> 0).
* ``context`` — free-form provenance carried through to per-sample results.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Sample(BaseModel):
    """A single domain-agnostic decision sample."""

    id: str = Field(..., description="Stable identifier for this sample.")
    complexity: float = Field(..., ge=0.0, description="Decision complexity x (>= 1 recommended).")
    value: float = Field(..., ge=-1.0, le=1.0, description="True value V(a) in [-1, 1].")
    judgment: float = Field(..., ge=-1.0, le=1.0, description="System judgment J(a) in [-1, 1].")
    weight: float = Field(1.0, gt=0.0, description="Importance weight w(a) (> 0).")
    context: Dict[str, Any] = Field(default_factory=dict, description="Free-form provenance metadata.")


class EvaluateParams(BaseModel):
    """ERH bound / selection parameters (all forwarded to ``erh_core``)."""

    tau: float = Field(0.3, ge=0.0, description="Mistake threshold |J - V| for a misjudgment.")
    C: float = Field(1.0, gt=0.0, description="ERH constant in |E(x)| <= C * x^(0.5 + eps).")
    epsilon: float = Field(0.1, ge=0.0, description="Epsilon in the exponent 0.5 + eps.")
    slack_factor: float = Field(1.5, gt=0.0, description="Practical slack multiplier on the bound.")
    allowed_violation_rate: float = Field(0.05, ge=0.0, le=1.0, description="Tolerated fraction of bound breaches.")
    baseline: str = Field("prime_theorem", description="Baseline B(x) type for compute_Pi_and_error.")
    importance_quantile: float = Field(0.9, ge=0.0, le=1.0, description="Top (1 - q) by weight kept as primes.")
    x_max: Optional[int] = Field(None, description="Max complexity grid; defaults to max observed complexity.")
    include_curves: bool = Field(False, description="Return Pi(x) / E(x) curves in the response.")


class EvaluateRequest(BaseModel):
    """Top-level evaluation request."""

    samples: List[Sample] = Field(..., description="Decision samples to evaluate.")
    params: EvaluateParams = Field(default_factory=EvaluateParams)
    judge_name: Optional[str] = Field(None, description="Label for the producing system, stored in the result.")


class Curve(BaseModel):
    """An (x, y) curve returned for visualization."""

    x: List[float]
    y: List[float]


class PrimeRef(BaseModel):
    """A sample flagged as an ethical prime (critical misjudgment)."""

    id: str
    complexity: float
    delta: float
    weight: float
    context: Dict[str, Any] = Field(default_factory=dict)


class EvaluateResponse(BaseModel):
    """Top-level evaluation result.

    Mirrors ``erh_core.analysis.erh_checks.ERHCheckResult`` plus a normalized
    ``risk_score`` (0-100) and optional curves / prime references.
    """

    erh_satisfied: bool
    risk_score: float = Field(..., description="Normalized risk in [0, 100]; higher = unhealthier.")
    violation_rate: float
    max_ratio: float
    bound_value: float
    estimated_exponent: float = Field(..., description="Fitted alpha in |E(x)| ~ x^alpha (~0.5 healthy).")
    r_squared: float
    num_samples: int
    num_primes: int
    bound_type: str
    judge_name: Optional[str] = None
    primes: List[PrimeRef] = Field(default_factory=list)
    pi_curve: Optional[Curve] = None
    error_curve: Optional[Curve] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "erh_engine"
    version: str
