"""
API routes for simulation management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from ..core.db import SessionLocal
from ..core.schemas import SimulationCreate, SimulationRead, SimulationResult
from ..core.models import Simulation, SimulationStatus
from ..core.time import utc_now
from ..services.simulation_service import run_simulation, save_simulation_results
from ..deps import get_db

router = APIRouter()

# Output directory for simulation results
SIMULATION_OUTPUT_DIR = Path(__file__).parent.parent.parent.parent.parent / "simulation" / "output"


def run_simulation_task(
    simulation_id: int,
    num_actions: int,
    complexity_dist: str,
    tau: float,
    db_session_factory=SessionLocal,
):
    """Background task to run simulation."""
    db = db_session_factory()
    try:
        # Update status to running
        sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if sim:
            sim.status = SimulationStatus.RUNNING
            db.commit()

        # Run simulation
        results = run_simulation(
            num_actions=num_actions,
            complexity_dist=complexity_dist,
            tau=tau,
        )

        # Save results
        result_path = save_simulation_results(
            results,
            SIMULATION_OUTPUT_DIR,
            simulation_id=simulation_id,
        )

        # Update simulation record
        sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if sim:
            sim.status = SimulationStatus.COMPLETED
            sim.result_path = result_path
            sim.completed_at = utc_now()
            db.commit()

    except Exception as e:
        # Update status to failed
        sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if sim:
            sim.status = SimulationStatus.FAILED
            db.commit()
        raise e
    finally:
        db.close()


@router.post("/", response_model=SimulationRead, tags=["simulate"])
def create_simulation(
    sim_config: SimulationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Create and trigger a new simulation.
    
    The simulation runs in the background. Check status via GET /simulations/{id}
    """
    # Validate complexity_dist
    if sim_config.complexity_dist not in ("zipf", "uniform", "power_law"):
        raise HTTPException(
            status_code=400,
            detail="complexity_dist must be one of: zipf, uniform, power_law"
        )

    # Validate num_actions range
    if sim_config.num_actions < 100 or sim_config.num_actions > 10000:
        raise HTTPException(
            status_code=400,
            detail="num_actions must be between 100 and 10000"
        )

    # Create simulation record
    db_sim = Simulation(
        status=SimulationStatus.PENDING,
        config={
            "num_actions": sim_config.num_actions,
            "complexity_dist": sim_config.complexity_dist,
            "tau": sim_config.tau,
        },
    )
    db.add(db_sim)
    db.commit()
    db.refresh(db_sim)

    # Start background task
    background_tasks.add_task(
        run_simulation_task,
        db_sim.id,
        sim_config.num_actions,
        sim_config.complexity_dist,
        sim_config.tau,
        SessionLocal,
    )

    return db_sim


@router.get("/", response_model=List[SimulationRead], tags=["simulate"])
def list_simulations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all simulations."""
    simulations = db.query(Simulation).offset(skip).limit(limit).order_by(Simulation.created_at.desc()).all()
    return simulations


@router.get("/{simulation_id}", response_model=SimulationRead, tags=["simulate"])
def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific simulation by ID."""
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim


@router.get("/{simulation_id}/results", response_model=SimulationResult, tags=["simulate"])
def get_simulation_results(
    simulation_id: int,
    db: Session = Depends(get_db),
):
    """Get simulation results if available."""
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if sim.status != SimulationStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Simulation is not completed. Status: {sim.status}"
        )

    if not sim.result_path or not Path(sim.result_path).exists():
        raise HTTPException(status_code=404, detail="Simulation results not found")

    # Load results from file
    import json
    with open(sim.result_path, "r") as f:
        results = json.load(f)

    return SimulationResult(**results)


@router.get("/{simulation_id}/figures", tags=["simulate"])
def get_simulation_figures(
    simulation_id: int,
    db: Session = Depends(get_db),
):
    """Get list of figures generated for a simulation."""
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    # For now, return available figures from the output directory
    figures_dir = SIMULATION_OUTPUT_DIR / "figures"
    if not figures_dir.exists():
        return {"figures": []}

    figures = []
    for fig_file in figures_dir.glob("*.png"):
        figures.append({
            "name": fig_file.name,
            "path": f"/api/v1/simulations/{simulation_id}/figures/{fig_file.name}",
        })
    for fig_file in figures_dir.glob("*.pdf"):
        figures.append({
            "name": fig_file.name,
            "path": f"/api/v1/simulations/{simulation_id}/figures/{fig_file.name}",
        })

    return {"figures": figures}


@router.get("/{simulation_id}/figures/{filename}", tags=["simulate"])
def get_simulation_figure(
    simulation_id: int,
    filename: str,
    db: Session = Depends(get_db),
):
    """Get a specific figure file for a simulation."""
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    figures_dir = SIMULATION_OUTPUT_DIR / "figures"
    file_path = (figures_dir / filename).resolve()

    # Prevent path traversal
    if not str(file_path).startswith(str(figures_dir.resolve())):
        raise HTTPException(status_code=404, detail="Figure not found")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Figure not found")

    return FileResponse(file_path)

