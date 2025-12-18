from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base
from app.ingestion.mock_data import generate_mock_data


def test_generate_mock_data_creates_rows(tmp_path) -> None:
    """
    Basic sanity check for mock data generation.
    """
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        actions, judgments = generate_mock_data(db, num_projects=1, mrs_per_project=3, seed=123)
        assert actions == 3
        assert judgments == 3
    finally:
        db.close()


