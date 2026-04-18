"""
Script to generate drift monitoring plot for LaTeX inclusion.
"""
import matplotlib.pyplot as plt
from erh_core.core.temporal_erh import simulate_ethical_drift_scenario
from pathlib import Path
import os

def generate_drift_plot(save_path):
    print("Simulating Ethical Drift Scenario...")
    results = simulate_ethical_drift_scenario(time_steps=15, drift_start_time=5)
    
    times = [r['time'] for r in results]
    alphas = [r['alpha'] for r in results]
    biases = [r['bias'] for r in results]
    
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
    plt.savefig(save_path)
    print(f"Drift plot saved to {save_path}")

if __name__ == "__main__":
    output_dir = Path("simulation/output/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_drift_plot(output_dir / "drift_monitoring.png")
