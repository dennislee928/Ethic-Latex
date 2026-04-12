from __future__ import annotations

import logging
from collections import defaultdict
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# VUL-007: Maximum code snippet size (50 KB)
_MAX_CODE_SNIPPET_BYTES = 50_000

from ..core.schemas import AnalysisCurves, AnalysisSummary, CurvePoint, HeatmapCell, HeatmapResponse
from ..deps import get_db
from ..erh_security.code_complexity import calculate_code_complexity
from ..erh_security.mapping import build_erh_dataset
from ..erh_security.metrics import analyze_erh_structure, compute_delta


class CodeComplexityRequest(BaseModel):
    """Request body for code complexity analysis."""

    code_snippet: str
    method: Literal["cyclomatic", "halstead", "auto"] = "auto"


class CodeComplexityResponse(BaseModel):
    """Response with concrete complexity score c ∈ [1, 100]."""

    complexity: float
    method_used: str


class HealthMonitorResponse(BaseModel):
    """E(x) vs Riemann bound x^{1/2} for Health Monitor."""

    error_curve: list[CurvePoint]
    riemann_bound: list[CurvePoint]
    violation: bool
    violation_points: list[CurvePoint]


router = APIRouter()


@router.post("/complexity", response_model=CodeComplexityResponse, tags=["analysis"])
def analyze_code_complexity(request: CodeComplexityRequest) -> CodeComplexityResponse:
    """
    Compute Cyclomatic or Halstead complexity for a code snippet.

    Returns concrete x value in [1, 100] for use in ERH Security PoC.
    Use this instead of abstract MR-size complexity when code content is available.
    """
    # VUL-007: Validate input size to prevent DoS via large payloads.
    if len(request.code_snippet.encode("utf-8")) > _MAX_CODE_SNIPPET_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Code snippet too large (limit: {_MAX_CODE_SNIPPET_BYTES // 1000} KB).",
        )
    if not request.code_snippet.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")

    logger.debug("Analyzing code complexity with method=%s, size=%d bytes",
                 request.method, len(request.code_snippet.encode("utf-8")))
    complexity = calculate_code_complexity(
        request.code_snippet,
        method=request.method,
    )
    return CodeComplexityResponse(
        complexity=complexity,
        method_used=request.method,
    )


def _load_and_analyze(db: Session, judge_type: str) -> dict:
    samples = build_erh_dataset(db, judge_type=judge_type)
    if not samples:
        raise HTTPException(status_code=404, detail="No samples available for analysis.")
    return analyze_erh_structure(samples)


@router.get("/summary", response_model=AnalysisSummary, tags=["analysis"])
def get_summary(
    judge_type: Literal["PIPELINE", "HUMAN", "COMBINED"] = Query("COMBINED"),
    db: Session = Depends(get_db),
) -> AnalysisSummary:
    """
    High-level ERH summary for a given judge type.
    """
    result = _load_and_analyze(db, judge_type=judge_type)
    growth = result.get("growth") or {}

    return AnalysisSummary(
        judge_type=judge_type,
        num_samples=int(result.get("num_samples", 0)),
        num_primes=int(result.get("num_primes", 0)),
        estimated_alpha=float(growth.get("alpha")) if "alpha" in growth else None,
        r_squared=float(growth.get("r_squared")) if "r_squared" in growth else None,
    )


@router.get("/curves", response_model=AnalysisCurves, tags=["analysis"])
def get_curves(
    judge_type: Literal["PIPELINE", "HUMAN", "COMBINED"] = Query("COMBINED"),
    db: Session = Depends(get_db),
) -> AnalysisCurves:
    """
    Return Pi(x) and error E(x) curves for plotting.
    """
    result = _load_and_analyze(db, judge_type=judge_type)
    pi_raw = result.get("pi_curve") or []
    err_raw = result.get("error_curve") or []

    pi_curve = [CurvePoint(x=float(p[0]), y=float(p[1])) for p in pi_raw]
    error_curve = [CurvePoint(x=float(e[0]), y=float(e[1])) for e in err_raw]

    return AnalysisCurves(pi_curve=pi_curve, error_curve=error_curve)


@router.get("/health", response_model=HealthMonitorResponse, tags=["analysis"])
def get_health_monitor(
    judge_type: Literal["PIPELINE", "HUMAN", "COMBINED"] = Query("COMBINED"),
    db: Session = Depends(get_db),
) -> HealthMonitorResponse:
    """
    Health Monitor: E(x) vs Riemann bound x^{1/2}.
    Triggers alert if |E(x)| > C·x^{1/2} (structural hallucination).
    """
    result = _load_and_analyze(db, judge_type=judge_type)
    err_raw = result.get("error_curve") or []
    error_curve = [CurvePoint(x=float(e[0]), y=float(e[1])) for e in err_raw]
    if not error_curve:
        return HealthMonitorResponse(
            error_curve=[],
            riemann_bound=[],
            violation=False,
            violation_points=[],
        )
    x_max = max(p.x for p in error_curve)
    scale = max(1e-6, max(abs(p.y) for p in error_curve) / max(1e-6, x_max**0.5))
    riemann_bound = [
        CurvePoint(x=float(x), y=float(scale * (x**0.5)))
        for x in [p.x for p in error_curve]
    ]
    violation_points = [
        p for p, b in zip(error_curve, riemann_bound)
        if abs(p.y) > b.y + 1e-6
    ]
    violation = len(violation_points) > 0
    return HealthMonitorResponse(
        error_curve=error_curve,
        riemann_bound=riemann_bound,
        violation=violation,
        violation_points=violation_points,
    )


@router.get("/heatmap", response_model=HeatmapResponse, tags=["analysis"])
def get_heatmap(
    judge_type: Literal["PIPELINE", "HUMAN", "COMBINED"] = Query("COMBINED"),
    bins: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> HeatmapResponse:
    """
    Coarse heatmap of average delta per complexity bin.
    """
    samples = build_erh_dataset(db, judge_type=judge_type)
    if not samples:
        raise HTTPException(status_code=404, detail="No samples available for analysis.")

    min_c = min(s.complexity for s in samples)
    max_c = max(s.complexity for s in samples)
    if min_c == max_c:
        width = 1.0
    else:
        width = (max_c - min_c) / float(bins)

    buckets: dict[int, list[float]] = defaultdict(list)
    for s in samples:
        idx = 0 if width == 0 else int((s.complexity - min_c) / width)
        if idx >= bins:
            idx = bins - 1
        buckets[idx].append(compute_delta(s))

    cells: list[HeatmapCell] = []
    for idx, deltas in buckets.items():
        center = float(min_c + (idx + 0.5) * width)
        mean_delta = float(sum(deltas) / len(deltas)) if deltas else 0.0
        cells.append(
            HeatmapCell(
                complexity_bin=center,
                delta_mean=mean_delta,
                count=len(deltas),
            )
        )

    return HeatmapResponse(judge_type=judge_type, cells=cells)


