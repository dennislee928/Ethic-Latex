import json

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base
from app.core.models import Simulation, SimulationStatus
from app.routers import simulate as simulate_router


def test_run_simulation_task_uses_session_factory(monkeypatch, tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'simulate.db'}")
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    with testing_session_local() as db:
        sim = Simulation(
            status=SimulationStatus.PENDING,
            config={"num_actions": 100, "complexity_dist": "zipf", "tau": 0.3},
        )
        db.add(sim)
        db.commit()
        db.refresh(sim)
        simulation_id = sim.id

    fake_results = {
        "mistake_rate": 0.1,
        "ethical_primes_count": 3,
        "analysis": {
            "estimated_exponent": 0.5,
            "alpha_ci_low": 0.45,
            "alpha_ci_high": 0.55,
            "erh_satisfied": True,
            "r_squared": 0.99,
            "growth_rate": "square_root",
        },
        "config": {"num_actions": 100, "complexity_dist": "zipf", "tau": 0.3},
    }

    monkeypatch.setattr(simulate_router, "run_simulation", lambda **_: fake_results)

    def fake_save_simulation_results(results, output_dir, simulation_id=None):
        path = tmp_path / f"sim_result_{simulation_id}.json"
        path.write_text(json.dumps(results), encoding="utf-8")
        return str(path)

    monkeypatch.setattr(simulate_router, "save_simulation_results", fake_save_simulation_results)

    simulate_router.run_simulation_task(
        simulation_id=simulation_id,
        num_actions=100,
        complexity_dist="zipf",
        tau=0.3,
        db_session_factory=testing_session_local,
    )

    with testing_session_local() as db:
        sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        assert sim is not None
        assert sim.status == SimulationStatus.COMPLETED
        assert sim.result_path is not None
