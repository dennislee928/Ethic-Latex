from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.models import Action, GroundTruth, Importance, Judgment
from .gitlab_client import GitLabClient


def _find_or_create_action(
    db: Session,
    project_id: int,
    mr: dict,
) -> Action:
    stmt = select(Action).where(
        Action.project_id == project_id,
        Action.mr_iid == mr["iid"],
    )
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        return existing

    action = Action(
        project_id=project_id,
        mr_iid=mr["iid"],
        title=mr.get("title", f"MR !{mr['iid']}"),
        lines_changed=mr.get("changes_count") or 0,
        files_changed=0,
        services_touched=0,
        created_at=datetime.fromisoformat(mr["created_at"].replace("Z", "+00:00")),
    )
    db.add(action)
    db.flush()
    return action


def _upsert_judgment(
    db: Session,
    action: Action,
    pipeline_status: Optional[str],
    human_review_status: Optional[str],
    findings: Optional[dict],
) -> Judgment:
    stmt = select(Judgment).where(Judgment.action_id == action.id)
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        existing.pipeline_status = pipeline_status
        existing.human_review_status = human_review_status
        existing.findings_json = findings or {}
        return existing

    judgment = Judgment(
        action_id=action.id,
        judge_type="PIPELINE",
        pipeline_status=pipeline_status,
        human_review_status=human_review_status,
        findings_json=findings or {},
    )
    db.add(judgment)
    return judgment


def _ensure_ground_truth_and_importance(db: Session, action: Action) -> Tuple[GroundTruth, Importance]:
    gt_stmt = select(GroundTruth).where(GroundTruth.action_id == action.id)
    gt = db.execute(gt_stmt).scalar_one_or_none()
    if not gt:
        gt = GroundTruth(
            action_id=action.id,
            unresolved_high_count=0,
            post_incident_flag=False,
            incident_severity=None,
        )
        db.add(gt)

    imp_stmt = select(Importance).where(Importance.action_id == action.id)
    importance = db.execute(imp_stmt).scalar_one_or_none()
    if not importance:
        importance = Importance(
            action_id=action.id,
            asset_criticality=1,
            internet_exposed=False,
            service_name=None,
        )
        db.add(importance)

    return gt, importance


def ingest_from_gitlab(
    db: Session,
    client: GitLabClient,
    updated_after: Optional[str] = None,
) -> int:
    """
    Ingest GitLab merge requests and associated security information.

    Args:
        db: SQLAlchemy Session
        client: GitLabClient instance
        updated_after: optional ISO-8601 string to filter recent MRs

    Returns:
        Number of Actions processed (created or updated).
    """
    projects = client.list_projects()
    processed = 0

    for project in projects:
        project_id = project["id"]
        mrs = client.list_merge_requests(project_id=project_id, updated_after=updated_after)

        for mr in mrs:
            action = _find_or_create_action(db, project_id, mr)

            # Get latest pipeline for MR, if any
            pipelines = client.get_pipelines_for_mr(project_id=project_id, mr_iid=mr["iid"])
            pipeline_status = None
            findings = None

            if pipelines:
                latest_pipeline = sorted(pipelines, key=lambda p: p.get("id", 0))[-1]
                pipeline_status = latest_pipeline.get("status")
                pipeline_id = latest_pipeline.get("id")
                if pipeline_id is not None:
                    try:
                        findings = client.get_security_reports(project_id=project_id, pipeline_id=pipeline_id)
                    except Exception:
                        # In many deployments security reports endpoint is disabled;
                        # swallow errors here and keep ingestion best-effort.
                        findings = {}

            _upsert_judgment(
                db=db,
                action=action,
                pipeline_status=pipeline_status,
                human_review_status=None,
                findings=findings,
            )

            _ensure_ground_truth_and_importance(db, action)
            processed += 1

    db.commit()
    return processed


