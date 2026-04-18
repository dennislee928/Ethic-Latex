#!/usr/bin/env python3
"""
Simulate 20 cases based on .ignore_ref/3.md categories.
Outputs JSON results to simulation/output/cases_20/
"""

import os
import json
import numpy as np
from pathlib import Path
import sys

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from erh_core.core.action_space import generate_world, Action
from erh_core.core.judgement_system import (
    BiasedJudge, NoisyJudge, ConservativeJudge, RadicalJudge, 
    evaluate_judgement, compute_judgment_metrics
)
from erh_core.core.ethical_primes import select_ethical_primes, compute_Pi_and_error, analyze_error_growth
from erh_core.core.algebraic_primes import select_primes_by_singularity, get_manifold_topology_metrics

CASES = [
    # 1. Judiciary & Security
    {"name": "Parole_Board", "cat": "Judiciary", "bias": 0.2, "noise": 0.1, "complex_dep": 0.4},
    {"name": "Terrorism_Screening", "cat": "Judiciary", "bias": 0.5, "noise": 0.4, "complex_dep": 0.8},
    {"name": "CPS_Child_Welfare", "cat": "Judiciary", "bias": 0.3, "noise": 0.2, "complex_dep": 0.6},
    
    # 2. Medical Ethics
    {"name": "ER_Triage", "cat": "Medical", "bias": 0.1, "noise": 0.3, "complex_dep": 0.3},
    {"name": "Organ_Matching", "cat": "Medical", "bias": 0.05, "noise": 0.1, "complex_dep": 0.2},
    {"name": "Mental_Health_Crisis", "cat": "Medical", "bias": 0.4, "noise": 0.5, "complex_dep": 0.7},
    
    # 3. Finance & Distribution
    {"name": "Micro_finance", "cat": "Finance", "bias": 0.25, "noise": 0.15, "complex_dep": 0.5},
    {"name": "Insurance_Pricing", "cat": "Finance", "bias": 0.15, "noise": 0.1, "complex_dep": 0.4},
    {"name": "Welfare_Eligibility", "cat": "Finance", "bias": 0.2, "noise": 0.2, "complex_dep": 0.6},
    
    # 4. HR & Workplace
    {"name": "Resume_Screening", "cat": "HR", "bias": 0.35, "noise": 0.1, "complex_dep": 0.5},
    {"name": "Performance_Evaluation", "cat": "HR", "bias": 0.2, "noise": 0.2, "complex_dep": 0.4},
    
    # 5. Digital Governance
    {"name": "Hate_Speech", "cat": "Governance", "bias": 0.45, "noise": 0.3, "complex_dep": 0.9},
    {"name": "Smart_Grid", "cat": "Governance", "bias": 0.05, "noise": 0.2, "complex_dep": 0.1},
    {"name": "Refugee_Status", "cat": "Governance", "bias": 0.3, "noise": 0.25, "complex_dep": 0.7},
    
    # 6. Education
    {"name": "Admission_Evaluation", "cat": "Education", "bias": 0.25, "noise": 0.15, "complex_dep": 0.4},
    {"name": "AES_Essay_Scoring", "cat": "Education", "bias": 0.15, "noise": 0.35, "complex_dep": 0.6},
    
    # 7. Emerging Risks (LLM)
    {"name": "Code_Vulnerability_SAST", "cat": "LLM", "bias": 0.1, "noise": 0.2, "complex_dep": 0.8},
    {"name": "Copyright_Compliance", "cat": "LLM", "bias": 0.2, "noise": 0.1, "complex_dep": 0.7},
    {"name": "Fake_News_Detection", "cat": "LLM", "bias": 0.3, "noise": 0.4, "complex_dep": 0.9},
    {"name": "Edge_AI_Decision", "cat": "LLM", "bias": 0.15, "noise": 0.5, "complex_dep": 0.4},
]

def run_simulation(case):
    print(f"Running simulation for: {case['name']} ({case['cat']})")
    
    # Generate actions with multidimensional values (3 dims: Fairness, Privacy, Safety)
    actions = generate_world(
        num_actions=1000, 
        complexity_dist="zipf", 
        dimensions=3,
        random_seed=42
    )
    
    # Create judge
    judge = BiasedJudge(
        bias_strength=case['bias'],
        noise_scale=case['noise'],
        complexity_dependency=case['complex_dep'],
        name=case['name']
    )
    
    # Evaluate
    evaluate_judgement(actions, judge, tau=0.3)
    
    # Select primes (Algebraic Primes)
    primes = select_primes_by_singularity(actions)
    
    # Compute ERH metrics
    Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
    analysis = analyze_error_growth(E_x, x_vals)
    
    # Topology metrics
    topology = get_manifold_topology_metrics(actions)
    
    # Results
    result = {
        "case": case['name'],
        "category": case['cat'],
        "config": {
            "complexity_dist": "zipf",
            "num_actions": 1000,
            **case
        },
        "metrics": {
            "mistake_rate": float(np.mean([a.mistake_flag for a in actions])),
            "ethical_primes_count": len(primes),
            "estimated_exponent": analysis.get('estimated_exponent'),
            "erh_satisfied": analysis.get('erh_satisfied'),
            "manifold_roughness": topology['manifold_roughness'],
            "singularity_density": topology['singularity_density']
        },
        "timestamp": os.path.getmtime(__file__)
    }
    
    return result

def save_summary(all_results, output_dir):
    """Save aggregate summary by category and detailed per-case metrics."""
    categories = {}
    detailed = {}
    for res in all_results:
        cat = res['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(res['metrics'])
        
        # Store detailed metrics for each specific case
        detailed[res['case']] = {
            "mistake_rate": res['metrics']['mistake_rate'],
            "ethical_primes_count": res['metrics']['ethical_primes_count'],
            "estimated_exponent": res['metrics']['estimated_exponent'],
            "erh_satisfied": res['metrics']['erh_satisfied']
        }
    
    summary = {"categories": {}, "detailed": detailed}
    for cat, metrics_list in categories.items():
        summary["categories"][cat] = {
            "mistake_rate": float(np.mean([m['mistake_rate'] for m in metrics_list])),
            "ethical_primes_count": float(np.mean([m['ethical_primes_count'] for m in metrics_list])),
            "estimated_exponent": float(np.mean([m['estimated_exponent'] for m in metrics_list])),
            "erh_satisfied_rate": float(np.mean([1.0 if m['erh_satisfied'] else 0.0 for m in metrics_list]))
        }
    
    # Advanced metrics from a representative run (e.g. Hate_Speech)
    hate_speech = next((r for r in all_results if r['case'] == "Hate_Speech"), all_results[0])
    summary["advanced"] = {
        "manifold_roughness": hate_speech['metrics']['manifold_roughness'],
        "singularity_density": hate_speech['metrics']['singularity_density'],
    }
    
    # Simulate one drift run for the final alpha
    from erh_core.core.temporal_erh import simulate_ethical_drift_scenario
    drift = simulate_ethical_drift_scenario(time_steps=5, drift_start_time=2)
    summary["advanced"]["drift_alpha_final"] = drift[-1]['alpha']

    with open(output_dir / "cases_20_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved to {output_dir / 'cases_20_summary.json'}")

def main():
    output_dir = ROOT / "simulation" / "output" / "cases_20"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_results = []
    for case in CASES:
        res = run_simulation(case)
        all_results.append(res)
        
        with open(output_dir / f"sim_result_{case['name']}.json", "w") as f:
            json.dump(res, f, indent=2)
            
    save_summary(all_results, output_dir)
    print(f"\nCompleted 20 simulations. Results saved to {output_dir}")

if __name__ == "__main__":
    main()
