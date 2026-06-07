"""
Demonstration of Dynamic ERH (Ethical Drift) and Algebraic Primes (Singularities).

This example shows:
1. Detecting Ethical Drift over time as the judge becomes more biased.
2. Identifying Algebraic Primes as "singularities" on the moral manifold.
"""

import numpy as np
import matplotlib.pyplot as plt
from erh_core.core.temporal_erh import simulate_ethical_drift_scenario
from erh_core.core.action_space import generate_world
from erh_core.core.judgement_system import BiasedJudge, evaluate_judgement
from erh_core.core.algebraic_primes import compute_ethical_curvature, select_primes_by_singularity

def plot_drift_results(drift_results):
    times = [r['time'] for r in drift_results]
    alphas = [r['alpha'] for r in drift_results]
    biases = [r['bias'] for r in drift_results]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = 'tab:blue'
    ax1.set_xlabel('Time Step')
    ax1.set_ylabel('Alpha Index (Error Growth)', color=color)
    ax1.plot(times, alphas, 'o-', color=color, label='Alpha')
    ax1.axhline(y=0.5, color='r', linestyle='--', label='ERH Limit (0.5)')
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Judge Bias Strength', color=color)
    ax2.plot(times, biases, 's--', color=color, label='Bias')
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Ethical Drift Monitoring: Alpha Index vs. Systemic Bias')
    fig.tight_layout()
    plt.savefig('drift_monitoring.png')
    print("Drift plot saved to drift_monitoring.png")

def demo_singularities():
    print("\nDemonstrating Algebraic Primes (Singularities)...")
    # Generate world with a "glitch" complexity level
    actions = generate_world(num_actions=1000, complexity_dist='zipf', random_seed=42)
    judge = BiasedJudge(bias_strength=0.1, noise_scale=0.1)
    evaluate_judgement(actions, judge)
    
    # Inject a "singularity" - extreme errors at complexity 50
    for a in actions:
        if a.c == 50:
            a.J = a.V + 0.8  # Large error
            a.delta = a.J - a.V
            a.mistake_flag = 1
            
    curvature = compute_ethical_curvature(actions)
    primes = select_primes_by_singularity(actions)
    
    print(f"Detected {len(primes)} singularity-based primes.")
    print(f"Singularity complexity levels in primes: {sorted(list(set(p.c for p in primes)))}")
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 101), np.abs(curvature), label='Ethical Curvature')
    plt.axvline(x=50, color='r', linestyle='--', label='Injected Singularity')
    plt.title('Ethical Curvature (Moral Manifold Analysis)')
    plt.xlabel('Complexity')
    plt.ylabel('|Curvature|')
    plt.legend()
    plt.savefig('ethical_curvature.png')
    print("Curvature plot saved to ethical_curvature.png")

if __name__ == "__main__":
    print("Simulating Ethical Drift Scenario...")
    results = simulate_ethical_drift_scenario(time_steps=15, drift_start_time=5)
    plot_drift_results(results)
    
    demo_singularities()
