from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy.orm import Session

from ..core.models import Action, GroundTruth, Importance, Judgment


def _random_title(idx: int) -> str:
    prefixes = ["Refactor", "Fix", "Feature", "Chore", "Security patch"]
    targets = ["auth", "payment", "CI", "API gateway", "user profile", "logging"]
    return f"{random.choice(prefixes)} {random.choice(targets)} #{idx}"


def generate_mock_data(
    db: Session,
    num_projects: int = 2,
    mrs_per_project: int = 10,
    seed: int | None = None,
) -> Tuple[int, int]:
    """
    Generate synthetic Actions, Judgments, GroundTruth and Importance rows.

    Returns:
        (num_actions, num_judgments)
    """
    if seed is not None:
        random.seed(seed)

    now = datetime.utcnow()
    total_actions = 0
    total_judgments = 0

    for project_idx in range(1, num_projects + 1):
        project_id = 1000 + project_idx
        for mr_idx in range(1, mrs_per_project + 1):
            # Simple time spread
            created_at = now - timedelta(days=random.randint(0, 90))

            action = Action(
                project_id=project_id,
                mr_iid=mr_idx,
                title=_random_title(mr_idx),
                lines_changed=random.randint(5, 2000),
                files_changed=random.randint(1, 40),
                services_touched=random.randint(1, 5),
                created_at=created_at,
            )
            db.add(action)
            db.flush()  # ensure action.id is available

            # Judgment: pretend all MRs have a CI pipeline result
            pipeline_status = random.choice(["success", "failed", "canceled"])
            human_status = random.choice(["approved", "rejected", "pending"])

            judgment = Judgment(
                action_id=action.id,
                judge_type="COMBINED",
                pipeline_status=pipeline_status,
                human_review_status=human_status,
                findings_json={},
            )
            db.add(judgment)

            # Ground truth proxy: some MRs lead to incidents
            post_incident = random.random() < 0.1
            unresolved_high = random.randint(0, 5) if post_incident else random.randint(0, 2)

            ground_truth = GroundTruth(
                action_id=action.id,
                unresolved_high_count=unresolved_high,
                post_incident_flag=post_incident,
                incident_severity=random.choice(["low", "medium", "high"]),
            )
            db.add(ground_truth)

            # Importance: vary criticality and exposure
            importance = Importance(
                action_id=action.id,
                asset_criticality=random.randint(1, 5),
                internet_exposed=random.random() < 0.5,
                service_name=random.choice(
                    ["auth-service", "payments", "user-service", "admin", "gateway"]
                ),
            )
            db.add(importance)

            total_actions += 1
            total_judgments += 1

    db.commit()
    return total_actions, total_judgments


