from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config import get_settings
from ..deps import get_db
from ..ingestion.gitlab_client import GitLabClient, GitLabClientError
from ..ingestion.gitlab_ingest import ingest_from_gitlab
from ..ingestion.mock_data import generate_mock_data

router = APIRouter()

# Add project root for simulation imports
_erh_root = Path(__file__).resolve().parents[4]
if str(_erh_root) not in sys.path:
    sys.path.insert(0, str(_erh_root))


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


def _load_huggingface(max_samples: int = 50, dataset: str = "ethics_commonsense") -> dict:
    """Load HuggingFace dataset and build J_ij matrix."""
    try:
        from simulation.real_data.huggingface_loader import load_and_build_J
        J, V = load_and_build_J(dataset=dataset, max_samples=max_samples)
        return {
            "dataset": dataset,
            "J_shape": list(J.shape),
            "V_shape": list(V.shape) if V is not None else None,
        }
    except ImportError:
        return {"error": "simulation.real_data.huggingface_loader not available"}


def _load_aita(limit: int = 20, use_firecrawl: bool = False) -> dict:
    """Load AITA-style data."""
    try:
        from simulation.real_data.aita_loader import load_aita_empirical
        rows = load_aita_empirical(limit=limit, use_firecrawl=use_firecrawl)
        return {"count": len(rows), "samples": [{"V": r.get("V"), "verdict": r.get("verdict")} for r in rows[:5]]}
    except ImportError:
        return {"error": "simulation.real_data.aita_loader not available"}


@router.post(
    "/huggingface",
    summary="Ingest HuggingFace ethics dataset",
    tags=["ingestion"],
)
def ingest_huggingface(
    dataset: Literal["ethics_commonsense", "social_i_qa", "moral_stories"] = Query(
        "ethics_commonsense", description="Dataset name"
    ),
    max_samples: int = Query(50, ge=1, le=500),
) -> dict:
    """Load HuggingFace dataset and build interaction matrix J_ij for Ising model."""
    return _load_huggingface(max_samples=max_samples, dataset=dataset)


@router.post(
    "/aita",
    summary="Ingest Reddit r/AmItheAsshole data (Firecrawl or stub)",
    tags=["ingestion"],
)
def ingest_aita(
    limit: int = Query(20, ge=1, le=100),
    use_firecrawl: bool = Query(False, description="Use Firecrawl for live scrape"),
) -> dict:
    """Load AITA-style empirical moral values V(a)."""
    return _load_aita(limit=limit, use_firecrawl=use_firecrawl)


