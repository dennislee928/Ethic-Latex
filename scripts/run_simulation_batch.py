#!/usr/bin/env python3
"""
Batch Simulation Runner
Execute ERH simulations with configurable parameters and save results to JSON/CSV.
Supports parallel execution via multiprocessing for CI/CD pipelines.
Modes: judge (default) = judge-based ERH analysis; abm = Agent-Based Model simulation.
"""

import argparse
import json
import multiprocessing
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure simulation module is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Also add erh_core if it exists
erh_core_path = os.path.join(project_root, "erh_core")
if os.path.exists(erh_core_path) and erh_core_path not in sys.path:
    sys.path.insert(0, erh_core_path)

from simulation.core import (
    generate_world,
    BiasedJudge,
    evaluate_judgement,
    select_ethical_primes,
    compute_Pi_and_error,
    analyze_error_growth,
)
try:
    from erh_core.core.output_writer import save_json_result
except ImportError:
    from simulation.core.output_writer import save_json_result  # type: ignore


def _run_single_trial_abm(trial_id: int, config: dict) -> dict:
    """Worker for ABMSimulator mode: run one ABM trial and return metrics."""
    try:
        from erh_core.core.abm_simulator import ABMSimulator
    except ImportError:
        from simulation.core import ABMSimulator  # type: ignore
    n_agents = config.get("n_agents", 50)
    n_steps = config.get("steps", 100)
    sim = ABMSimulator(num_agents=n_agents)
    results = sim.run_simulation(num_time_steps=n_steps)
    erh_history = results.get("erh_history", [])
    final_error = 0.0
    quantum_energy = 0.0
    evs = 0.0
    if erh_history:
        last = erh_history[-1]
        analysis = last.get("analysis", {})
        E_x = last.get("E_x", [])
        if E_x is not None and len(E_x) > 0:
            import numpy as np
            final_error = float(np.mean(np.abs(E_x)))
        erh_satisfied = analysis.get("erh_satisfied", False)
        alpha = analysis.get("estimated_exponent", 0.5)
        stability = 1.0 if erh_satisfied else max(0, 0.5 - alpha)
        evs = stability * 0.9  # Placeholder; full EVS needs fairness, polarization
    return {
        "id": trial_id,
        "final_error": final_error,
        "social_tension": quantum_energy,
        "evs": evs,
        "erh_history_len": len(erh_history),
    }


def _run_single_config(config: dict, output_dir: str) -> str:
    """Worker function for a single simulation run (used by multiprocessing)."""
    sim_id = config.get("id", 0)
    num_actions = config.get("num_actions", 1000)
    complexity_dist = config.get("complexity_dist", "zipf")
    seed = config.get("seed", 42 + sim_id)

    start_time = time.time()
    actions = generate_world(
        num_actions=num_actions,
        complexity_dist=complexity_dist,
        random_seed=seed,
    )
    judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)
    evaluate_judgement(actions, judge, tau=0.3)
    primes = select_ethical_primes(actions, importance_quantile=0.9)
    Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
    analysis = analyze_error_growth(E_x, x_vals)
    duration = time.time() - start_time
    mistakes = sum(1 for a in actions if a.mistake_flag)

    result = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "id": sim_id,
            "num_actions": num_actions,
            "complexity_dist": complexity_dist,
            "seed": seed,
        },
        "metrics": {
            "duration_seconds": duration,
            "total_actions": len(actions),
            "mistakes_count": mistakes,
            "mistake_rate": mistakes / len(actions),
            "ethical_primes_count": len(primes),
            "erh_satisfied": bool(analysis.get("erh_satisfied", False)),
            "estimated_exponent": analysis.get("estimated_exponent"),
        },
    }
    path = save_json_result(result, output_dir)
    stability = 1.0 - (mistakes / len(actions)) if actions else 0.0
    return f"Sim {sim_id} completed. Stability: {stability:.3f} -> {path}"


def run_simulation(args):
    """Run a single simulation configuration (legacy / non-parallel path)."""
    print(
        f"Starting simulation: N={args.num_actions}, Dist={args.complexity_dist}, Seed={args.seed}"
    )
    start_time = time.time()

    actions = generate_world(
        num_actions=args.num_actions,
        complexity_dist=args.complexity_dist,
        random_seed=args.seed,
    )
    judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)
    evaluate_judgement(actions, judge, tau=0.3)
    primes = select_ethical_primes(actions, importance_quantile=0.9)
    Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
    analysis = analyze_error_growth(E_x, x_vals)
    duration = time.time() - start_time
    mistakes = sum(1 for a in actions if a.mistake_flag)

    result = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "num_actions": args.num_actions,
            "complexity_dist": args.complexity_dist,
            "seed": args.seed,
        },
        "metrics": {
            "duration_seconds": duration,
            "total_actions": len(actions),
            "mistakes_count": mistakes,
            "mistake_rate": mistakes / len(actions),
            "ethical_primes_count": len(primes),
            "erh_satisfied": bool(analysis.get("erh_satisfied", False)),
            "estimated_exponent": analysis.get("estimated_exponent"),
        },
    }
    return result


def main():
    parser = argparse.ArgumentParser(description="ERH Batch Simulation Runner")
    parser.add_argument(
        "--mode",
        type=str,
        default="judge",
        choices=["judge", "abm"],
        help="Simulation mode: judge (default) or abm (Agent-Based Model)",
    )
    parser.add_argument(
        "--num-actions", type=int, default=1000, help="Number of actions (judge mode)"
    )
    parser.add_argument(
        "--agents", type=int, default=50, help="Number of agents (abm mode)"
    )
    parser.add_argument(
        "--steps", type=int, default=100, help="Time steps (abm mode)"
    )
    parser.add_argument(
        "--trials", type=int, default=4, help="Number of trials (abm mode)"
    )
    parser.add_argument(
        "--complexity-dist",
        type=str,
        default="zipf",
        choices=["zipf", "uniform", "power_law"],
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Output directory",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path for aggregated JSON output (abm mode or when --instances>1). Default: simulation/output/batch_results.json",
    )
    parser.add_argument(
        "--instances",
        type=int,
        default=1,
        help="Number of parallel simulation instances (multiprocessing)",
    )
    parser.add_argument(
        "--configs",
        type=str,
        default=None,
        help="Path to JSON config file (list of configs). If not set, uses --num-actions/--complexity-dist/--seed with --instances runs.",
    )
    parser.add_argument(
        "--real-data-only",
        action="store_true",
        help="Run only empirical validation (COMPAS, Adult) and skip judge/ABM simulation.",
    )

    args = parser.parse_args()

    # Real-data-only mode: run empirical validation script
    if args.real_data_only:
        run_emp = project_root / "scripts" / "run_empirical_validation.py"
        if run_emp.exists():
            import subprocess
            out_dir = args.output_dir or os.path.join(project_root, "simulation", "output")
            result = subprocess.run(
                [sys.executable, str(run_emp), "--output", str(Path(out_dir) / "real_world_results.json")],
                cwd=str(project_root),
                env={**os.environ, "PYTHONPATH": f"{project_root}:{os.path.join(project_root, 'erh_core')}"},
            )
            sys.exit(result.returncode)
        else:
            print("run_empirical_validation.py not found")
            sys.exit(1)

    # ABM mode
    if args.mode == "abm":
        config = {"n_agents": args.agents, "steps": args.steps}
        start_time = time.time()
        with multiprocessing.Pool() as pool:
            results = pool.starmap(_run_single_trial_abm, [(i, config) for i in range(args.trials)])
        duration = time.time() - start_time
        output_path = args.output or os.path.join(project_root, "simulation", "output", "batch_results.json")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump({"config": config, "results": results, "duration_seconds": duration}, f, indent=2)
        print(f"ABM batch completed in {duration:.2f}s ({args.trials} trials) -> {output_path}")
        return

    if args.instances <= 1 and args.configs is None:
        # Single-run path (backward compatible)
        try:
            result = run_simulation(args)
            path = save_json_result(result, args.output_dir)
            print(f"Results saved to {path}")
        except Exception as e:
            print(f"Error running simulation: {e}")
            sys.exit(1)
        return

    # Parallel batch path
    os.makedirs(args.output_dir, exist_ok=True)
    if args.configs and os.path.isfile(args.configs):
        with open(args.configs) as f:
            configs = json.load(f)
        if not isinstance(configs, list):
            configs = [configs]
        for i, c in enumerate(configs):
            if "id" not in c:
                c["id"] = i
    else:
        configs = [
            {
                "id": i,
                "num_actions": args.num_actions,
                "complexity_dist": args.complexity_dist,
                "seed": args.seed + i,
            }
            for i in range(args.instances)
        ]

    n_workers = min(args.instances, len(configs), multiprocessing.cpu_count())
    start_time = time.time()
    with multiprocessing.Pool(processes=n_workers) as pool:
        results = pool.starmap(
            _run_single_config,
            [(cfg, args.output_dir) for cfg in configs],
        )
    elapsed = time.time() - start_time
    print(f"Batch completed in {elapsed:.2f}s ({len(configs)} simulations)")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
