"""
UEBA insider-threat adapter (Phase 3).

Builds a per-user "behavioral convergence domain" from a baseline of events,
then measures how far subsequent events deviate. ERH flags when a user's
behavioral error term grows beyond the bound — the signature of a slow insider
drift rather than isolated noise.

Per event:
    complexity (x) = situational complexity (off-hours, sensitivity, volume)
    value (V)      = the user's normal/expected behavior (convergence center)
    judgment (J)   = the observed behavior
    delta = J - V  => behavioral deviation
    weight (w)     = data sensitivity / asset criticality

Live integration: events can be streamed from a SIEM/log source; here they are
supplied inline, mirroring ``erh-security-app/backend/app/ingestion`` (live
client + fixture fallback).
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from typing import Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..contracts.schemas import EvaluateParams, EvaluateRequest, EvaluateResponse, Sample
from ..engine import evaluate as run_evaluate

router = APIRouter(prefix="/v1/ueba", tags=["ueba"])


class UEBAEvent(BaseModel):
    id: Optional[str] = None
    user: str
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23).")
    bytes_downloaded: float = Field(0.0, ge=0.0)
    sensitive: bool = False
    is_baseline: bool = Field(
        False, description="True if this event belongs to the user's normal-behavior baseline."
    )


class UEBARequest(BaseModel):
    events: List[UEBAEvent]
    params: EvaluateParams = Field(default_factory=EvaluateParams)
    work_start: int = 9
    work_end: int = 18


def _user_baselines(events: List[UEBAEvent]) -> Dict[str, float]:
    """Mean download volume per user from baseline-flagged events."""
    by_user: Dict[str, List[float]] = defaultdict(list)
    for e in events:
        if e.is_baseline:
            by_user[e.user].append(e.bytes_downloaded)
    return {u: (statistics.mean(v) if v else 0.0) for u, v in by_user.items()}


def _off_hours(hour: int, work_start: int, work_end: int) -> bool:
    return hour < work_start or hour >= work_end


def events_to_samples(req: UEBARequest) -> List[Sample]:
    baselines = _user_baselines(req.events)
    samples: List[Sample] = []
    for i, e in enumerate(req.events):
        if e.is_baseline:
            continue
        base = baselines.get(e.user, 0.0)
        # Deviation in download volume, normalized & signed (more than usual = -).
        denom = base if base > 0 else 1.0
        volume_dev = min(2.0, max(0.0, (e.bytes_downloaded - base) / denom))
        off = _off_hours(e.hour, req.work_start, req.work_end)

        # V: expected (normal) behavior pole = +1. J drops with deviation signals.
        v = 1.0
        j = 1.0 - volume_dev - (0.6 if off else 0.0) - (0.4 if e.sensitive else 0.0)
        j = float(max(-1.0, min(1.0, j)))

        # Complexity: how unusual the *situation* is (off-hours + sensitive + size).
        complexity = 1.0 + (40.0 if off else 0.0) + (30.0 if e.sensitive else 0.0) + min(29.0, volume_dev * 15.0)
        weight = 1.0 + (4.0 if e.sensitive else 0.0)

        samples.append(
            Sample(
                id=e.id or f"ueba-{i}",
                complexity=float(min(100.0, complexity)),
                value=v,
                judgment=j,
                weight=weight,
                context={"user": e.user, "off_hours": off, "sensitive": e.sensitive},
            )
        )
    return samples


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_ueba(req: UEBARequest) -> EvaluateResponse:
    samples = events_to_samples(req)
    return run_evaluate(
        EvaluateRequest(samples=samples, params=req.params, judge_name="ueba")
    )
