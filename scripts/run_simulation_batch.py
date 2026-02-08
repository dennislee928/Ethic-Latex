#!/usr/bin/env python3
"""
Batch Simulation Runner
Execute ERH simulations with configurable parameters and save results to JSON/CSV.
Designed for use in CI/CD pipelines.
"""

import argparse
import json
import csv
import os
import sys
import time
from datetime import datetime

# Ensure simulation module is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Also add erh_core if it exists
erh_core_path = os.path.join(project_root, 'erh_core')
if os.path.exists(erh_core_path) and erh_core_path not in sys.path:
    sys.path.insert(0, erh_core_path)

from simulation.core import (
    generate_world,
    Action,
    BiasedJudge,
    evaluate_judgement,
    select_ethical_primes,
    compute_Pi_and_error,
    analyze_error_growth,
)
try:
    from simulation.core.output_writer import save_json_result
except ImportError:
    from erh_core.core.output_writer import save_json_result

def run_simulation(args):
    """Run a single simulation configuration."""
    print(f"Starting simulation: N={args.num_actions}, Dist={args.complexity_dist}, Seed={args.seed}")
    start_time = time.time()
    
    # 1. Generate World
    actions = generate_world(
        num_actions=args.num_actions,
        complexity_dist=args.complexity_dist,
        random_seed=args.seed
    )
    
    # 2. Judge (Hardcoded configuration for now, extendable via args)
    judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)
    evaluate_judgement(actions, judge, tau=0.3)
    
    # 3. Analyze
    primes = select_ethical_primes(actions, importance_quantile=0.9)
    Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
    analysis = analyze_error_growth(E_x, x_vals)
    
    duration = time.time() - start_time
    
    # 4. Metrics
    mistakes = sum(1 for a in actions if a.mistake_flag)
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "num_actions": args.num_actions,
            "complexity_dist": args.complexity_dist,
            "seed": args.seed
        },
        "metrics": {
            "duration_seconds": duration,
            "total_actions": len(actions),
            "mistakes_count": mistakes,
            "mistake_rate": mistakes / len(actions),
            "ethical_primes_count": len(primes),
            "erh_satisfied": bool(analysis.get("erh_satisfied", False)),
            "estimated_exponent": analysis.get("estimated_exponent")
        }
    }
    
    return result

def main():
    parser = argparse.ArgumentParser(description="ERH Batch Simulation Runner")
    parser.add_argument("--num-actions", type=int, default=1000, help="Number of actions")
    parser.add_argument("--complexity-dist", type=str, default="zipf", choices=["zipf", "uniform", "power_law"])
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output-dir", type=str, default="simulation_results", help="Output directory")
    
    args = parser.parse_args()
    
    try:
        result = run_simulation(args)
        path = save_json_result(result, args.output_dir)
        print(f"Results saved to {path}")
    except Exception as e:
        print(f"Error running simulation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
