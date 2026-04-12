from pathlib import Path

from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.core.models import Simulation, SimulationStatus
from app.main import app


client = TestClient(app)


def test_simulation_figures_use_fetchable_urls() -> None:
    project_root = Path(__file__).resolve().parents[3]
    figures_dir = project_root / "simulation" / "output" / "figures"
    figure_path = figures_dir / "test_simulate_router_asset.pdf"

    figures_dir.mkdir(parents=True, exist_ok=True)
    figure_path.write_bytes(b"%PDF-1.4\n% simulation asset\n")

    db = SessionLocal()
    simulation = Simulation(
        status=SimulationStatus.COMPLETED,
        config={"num_actions": 1000, "complexity_dist": "zipf", "tau": 0.3},
        result_path="simulation/output/result.json",
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)

    try:
        response = client.get(f"/api/v1/simulations/{simulation.id}/figures")

        assert response.status_code == 200
        payload = response.json()
        figure = next(item for item in payload["figures"] if item["name"] == figure_path.name)
        assert figure["path"].startswith(f"/api/v1/simulations/{simulation.id}/figures/")

        file_response = client.get(figure["path"])
        assert file_response.status_code == 200
    finally:
        db.delete(simulation)
        db.commit()
        db.close()
        figure_path.unlink(missing_ok=True)
