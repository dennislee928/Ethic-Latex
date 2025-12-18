from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base
from app.core.models import Action, GroundTruth, Importance, Judgment
from app.erh_security.mapping import (
    ErhSample,
    build_erh_dataset,
    compute_complexity,
    compute_ground_truth,
    compute_judgment,
    compute_weight,
)


def _make_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_compute_functions_monotonic() -> None:
    action = Action(
        project_id=1,
        mr_iid=1,
        title="test",
        lines_changed=1000,
        files_changed=10,
        services_touched=2,
    )
    gt = GroundTruth(action_id=1, unresolved_high_count=3, post_incident_flag=False)
    imp = Importance(action_id=1, asset_criticality=3, internet_exposed=True)
    j = Judgment(action_id=1, judge_type="COMBINED", pipeline_status="failed", human_review_status="approved")

    c = compute_complexity(action)
    v = compute_ground_truth(gt)
    w = compute_weight(imp)
    jv = compute_judgment(j, judge_type="COMBINED")

    assert 1.0 <= c <= 100.0
    assert -1.0 <= v <= 0.0
    assert w > 0.0
    assert -1.0 <= jv <= 1.0


def test_build_erh_dataset_creates_samples() -> None:
    db = _make_session()
    try:
        action = Action(
            project_id=1,
            mr_iid=1,
            title="test",
            lines_changed=500,
            files_changed=5,
            services_touched=1,
        )
        db.add(action)
        db.flush()

        gt = GroundTruth(action_id=action.id, unresolved_high_count=1, post_incident_flag=False)
        imp = Importance(action_id=action.id, asset_criticality=2, internet_exposed=False)
        j = Judgment(
            action_id=action.id,
            judge_type="PIPELINE",
            pipeline_status="success",
            human_review_status=None,
        )
        db.add_all([gt, imp, j])
        db.commit()

        samples = build_erh_dataset(db, judge_type="PIPELINE")
        assert len(samples) == 1
        s = samples[0]
        assert isinstance(s, ErhSample)
        assert s.action_id == action.id
    finally:
        db.close()


