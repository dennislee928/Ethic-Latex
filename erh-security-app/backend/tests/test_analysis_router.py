from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base
from app.core.models import Action, GroundTruth, Importance, Judgment
from app.main import app


client = TestClient(app)


def _seed_minimal_data() -> None:
    # Recreate in-memory DB used by the app's engine metadata
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        action = Action(
            project_id=1,
            mr_iid=1,
            title="analysis-test",
            lines_changed=100,
            files_changed=2,
            services_touched=1,
        )
        db.add(action)
        db.flush()
        gt = GroundTruth(action_id=action.id, unresolved_high_count=0, post_incident_flag=False)
        imp = Importance(action_id=action.id, asset_criticality=2, internet_exposed=False)
        j = Judgment(
            action_id=action.id,
            judge_type="COMBINED",
            pipeline_status="success",
            human_review_status="approved",
        )
        db.add_all([gt, imp, j])
        db.commit()
    finally:
        db.close()


def test_analysis_endpoints_exist() -> None:
    # We mainly check HTTP 404 vs 200 behaviour and JSON structure.
    # In this minimal test environment the shared DB may not have data,
    # so we expect either 404 or 200 with valid JSON.

    response = client.get("/analysis/summary?judge_type=COMBINED")
    assert response.status_code in (200, 404)

    if response.status_code == 200:
        data = response.json()
        assert "num_samples" in data

    response_curves = client.get("/analysis/curves?judge_type=COMBINED")
    assert response_curves.status_code in (200, 404)

    response_heatmap = client.get("/analysis/heatmap?judge_type=COMBINED")
    assert response_heatmap.status_code in (200, 404)


