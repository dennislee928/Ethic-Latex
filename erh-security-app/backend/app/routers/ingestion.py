from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config import get_settings
from ..deps import get_db
from ..ingestion.gitlab_client import GitLabClient, GitLabClientError
from ..ingestion.gitlab_ingest import ingest_from_gitlab
from ..ingestion.mock_data import generate_mock_data


router = APIRouter()


@router.post(
    "/run",
    summary="Trigger ingestion from GitLab or mock generator",
    tags=["ingestion"],
)
def run_ingestion(
    mode: Literal["gitlab", "mock"] = Query("mock", description="Ingestion mode"),
    updated_after: Optional[str] = Query(
        None,
        description="ISO-8601 timestamp string, e.g. 2024-01-01T00:00:00Z",
    ),
    db: Session = Depends(get_db),
) -> dict:
    """
    Run ingestion pipeline.

    - `mode=mock`: generate synthetic data locally (no external calls).
    - `mode=gitlab`: pull recent MRs and security results from a GitLab instance.
    """
    settings = get_settings()

    if mode == "mock":
        actions, judgments = generate_mock_data(db)
        return {
            "mode": "mock",
            "actions_created": actions,
            "judgments_created": judgments,
        }

    if not settings.gitlab_base_url:
        raise HTTPException(
            status_code=400,
            detail="gitlab_base_url is not configured; cannot run real GitLab ingestion.",
        )

    # Validate updated_after if provided
    if updated_after is not None:
        try:
            # We only validate format; GitLab still receives the original string.
            datetime.fromisoformat(updated_after.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid updated_after timestamp.") from exc

    client = GitLabClient(base_url=str(settings.gitlab_base_url), token=settings.gitlab_token)

    try:
        processed = ingest_from_gitlab(db=db, client=client, updated_after=updated_after)
    except GitLabClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "mode": "gitlab",
        "actions_processed": processed,
    }


