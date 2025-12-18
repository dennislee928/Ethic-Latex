from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_run_ingestion_mock_mode() -> None:
    """
    Smoke test: /ingestion/run in mock mode returns counts.
    """
    response = client.post("/ingestion/run?mode=mock")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "mock"
    assert data["actions_created"] > 0
    assert data["judgments_created"] > 0


