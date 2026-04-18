from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_assets_index_lists_root_pdfs_and_figures() -> None:
    project_root = Path(__file__).resolve().parents[3]
    figures_dir = project_root / "figures"
    simulation_figures_dir = project_root / "simulation" / "output" / "figures"
    figure_path = figures_dir / "test_assets_router_figure.pdf"
    simulation_figure_path = simulation_figures_dir / "test_assets_router_simulation_figure.pdf"

    figures_dir.mkdir(parents=True, exist_ok=True)
    simulation_figures_dir.mkdir(parents=True, exist_ok=True)
    figure_path.write_bytes(b"%PDF-1.4\n% asset figure\n")
    simulation_figure_path.write_bytes(b"%PDF-1.4\n% simulation figure\n")

    try:
        response = client.get("/assets/index")

        assert response.status_code == 200
        payload = response.json()
        assert any(doc["name"] == "ethical_riemann_hypothesis.pdf" for doc in payload["documents"])
        assert "figures" in payload
        assert any(fig["name"] == figure_path.name for fig in payload["figures"])
        assert any(fig["name"] == simulation_figure_path.name for fig in payload["figures"])
    finally:
        figure_path.unlink(missing_ok=True)
        simulation_figure_path.unlink(missing_ok=True)
