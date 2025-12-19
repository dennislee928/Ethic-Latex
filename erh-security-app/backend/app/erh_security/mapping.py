from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.models import Action, GroundTruth, Importance, Judgment


@dataclass
class ErhSample:
    """
    Minimal ERH sample used for downstream metrics.
    """

    complexity: float
    ground_truth_value: float
    weight: float
    judgment_value: float
    action_id: int


def compute_complexity(action: Action) -> float:
    """
    Combine basic MR size signals into a bounded complexity score c ∈ [1, 100].
    """
    lines = max(0, action.lines_changed or 0)
    files = max(0, action.files_changed or 0)
    services = max(0, action.services_touched or 0)

    raw = 1.0 + (lines / 1000.0 + files / 10.0 + services * 5.0)
    return float(min(100.0, raw))


def compute_ground_truth(gt: GroundTruth) -> float:
    """
    Map ground-truth security state to V(a) ∈ [-1, 1].
    """
    if gt.post_incident_flag:
        return -1.0

    unresolved = max(0, gt.unresolved_high_count or 0)
    penalty = 0.5 * min(1.0, unresolved / 5.0)
    return float(-penalty)


def compute_weight(importance: Importance) -> float:
    """
    Log-normal-like importance weight based on asset criticality and exposure.
    """
    crit = max(1, importance.asset_criticality or 1)
    exposed = 1 if importance.internet_exposed else 0
    exponent = 2.0 + crit * 0.5 + exposed
    return float(math.exp(exponent))


def compute_judgment(judgment: Judgment, judge_type: str = "COMBINED") -> float:
    """
    Map security pipeline/human review outcomes to J(a) ∈ [-1, 1].
    """
    jt = (judge_type or "COMBINED").upper()

    def from_pipeline(status: str | None) -> float:
        if not status:
            return 0.0
        status_l = status.lower()
        if status_l == "failed":
            return -1.0
        if status_l in {"canceled", "skipped"}:
            return 0.0
        # success or other “ok-ish” states
        return 1.0

    def from_human(status: str | None) -> float:
        if not status:
            return 0.0
        status_l = status.lower()
        if status_l == "rejected":
            return -1.0
        if status_l == "approved":
            return 1.0
        return 0.0

    pipeline_val = from_pipeline(judgment.pipeline_status)
    human_val = from_human(judgment.human_review_status)

    if jt == "PIPELINE":
        return pipeline_val
    if jt == "HUMAN":
        return human_val

    # COMBINED: simple average with slightly higher weight on pipeline
    num = 2.0 * pipeline_val + 1.0 * human_val
    den = 3.0
    return float(num / den)


def build_erh_dataset(db: Session, judge_type: str = "COMBINED") -> List[ErhSample]:
    """
    Build ERH-ready dataset from actions that have complete auxiliary data.
    """
    stmt = (
        select(Action, Judgment, GroundTruth, Importance)
        .join(Judgment, Judgment.action_id == Action.id)
        .join(GroundTruth, GroundTruth.action_id == Action.id)
        .join(Importance, Importance.action_id == Action.id)
    )
    rows = db.execute(stmt).all()

    samples: List[ErhSample] = []
    for action, judgment, gt, importance in rows:
        c = compute_complexity(action)
        v = compute_ground_truth(gt)
        w = compute_weight(importance)
        j = compute_judgment(judgment, judge_type=judge_type)
        samples.append(
            ErhSample(
                complexity=c,
                ground_truth_value=v,
                weight=w,
                judgment_value=j,
                action_id=action.id,
            )
        )

    return samples




