#!/usr/bin/env python3
"""
Batch Simulation Runner
Execute ERH simulations with configurable parameters and save results to JSON/CSV.
Supports parallel execution via multiprocessing for CI/CD pipelines.
"""

import argparse
import json
import multiprocessing
import os
import sys
import time
from datetime import datetime

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
        "--num-actions", type=int, default=1000, help="Number of actions"
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

    args = parser.parse_args()

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
