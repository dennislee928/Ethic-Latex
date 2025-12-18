from __future__ import annotations

from collections import defaultdict
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.schemas import AnalysisCurves, AnalysisSummary, CurvePoint, HeatmapCell, HeatmapResponse
from ..deps import get_db
from ..erh_security.mapping import build_erh_dataset
from ..erh_security.metrics import analyze_erh_structure, compute_delta


router = APIRouter()


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


