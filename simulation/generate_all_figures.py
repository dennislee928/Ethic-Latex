"""
Generate All Figures for the Paper

This script runs all simulations and generates publication-quality figures.
Run from repo root: python -m simulation.generate_all_figures

Usage:
    python -m simulation.generate_all_figures
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Ensure project root is on path (for erh_core when run as -m simulation.generate_all_figures)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from erh_core.core.action_space import generate_world
from erh_core.core.judgement_system import BiasedJudge, NoisyJudge, ConservativeJudge, RadicalJudge, batch_evaluate
from erh_core.core.ethical_primes import select_ethical_primes, compute_Pi_and_error, analyze_error_growth, compare_error_distributions
from simulation.analysis.zeta_function import (
    build_m_sequence,
    compute_spectrum,
    find_approximate_zeros,
    analyze_spectrum_peaks,
)
from simulation.analysis.statistics import compare_judges, generate_report
from simulation.visualization.plots import (
    setup_paper_style,
    plot_Pi_B_E,
    plot_error_growth,
    plot_multi_judge_errors,
    plot_spectrum,
    plot_zero_distribution,
    plot_complexity_distribution,
    plot_judge_comparison,
)

# Setup
setup_paper_style()
np.random.seed(42)

print("=" * 70)
print("ETHICAL RIEMANN HYPOTHESIS - FIGURE GENERATION")
print("=" * 70)
print()

# Ensure output directory exists (relative to script directory)
output_dir = os.path.join(script_dir, 'output', 'figures')
os.makedirs(output_dir, exist_ok=True)

print("[1/10] Generating action space (N=2000)...")
actions = generate_world(
    num_actions=2000,
    complexity_dist='zipf',
    complexity_range=(1, 100),
    moral_ambiguity_factor=0.3,
    random_seed=42
)
print(f"      Generated {len(actions)} actions")

print("\n[2/10] Creating judgment systems...")
judges = {
    'Biased': BiasedJudge(bias_strength=0.2, noise_scale=0.1),
    'Noisy': NoisyJudge(noise_scale=0.3),
    'Conservative': ConservativeJudge(threshold=0.5),
    'Radical': RadicalJudge(amplification=1.5)
}
try:
    from simulation.quantum import LocalQuantumJudge
    from simulation.core.judgement_system import QuantumJudge
    oracle = LocalQuantumJudge(shots=512, seed=42)
    judges['Quantum'] = QuantumJudge(quantum_oracle=oracle)
    print("      Added Quantum Judge (qiskit or NumPy fallback)")
except Exception as e:
    print(f"      Quantum Judge skipped: {e}")
print(f"      Created {len(judges)} judges")

print("\n[3/10] Evaluating all judges...")
results = batch_evaluate(actions, judges, tau=0.3)
print("      Evaluation complete")

# Print basic statistics
print("\n" + "=" * 70)
print("PRELIMINARY STATISTICS")
print("=" * 70)
comparison = compare_judges(results, X_max=100)
for name, metrics in comparison.items():
    if 'error' in metrics:
        print(f"\n{name}: ERROR - {metrics['error']}")
        continue
    print(f"\n{name}:")
    alpha = metrics['estimated_exponent']
    within_bound = alpha <= 0.5 + 0.15
    print(f"  Mistake rate: {metrics['mistake_rate']:.3f}")
    print(f"  Num primes: {metrics['num_primes']}")
    print(f"  Estimated exponent α: {alpha:.3f}")
    print(
        "  Within ERH-style bound (α ≲ 0.5)? "
        f"{'Yes' if within_bound else 'No'}"
    )
    # analysis['erh_satisfied'] still encodes \"close to α ≈ 0.5\"
    print(
        "  Close to ERH-style target (α ≈ 0.5)? "
        f"{'Yes [target-like]' if metrics['erh_satisfied'] else 'No'}"
    )
    print(f"  Growth rate: {metrics['growth_rate']}")

print("\n" + "=" * 70)
print("GENERATING FIGURES")
print("=" * 70)

# Figure 1: Basic Π(x), B(x), E(x) for Biased Judge
print("\n[4/11] Figure 1: Π(x), B(x), E(x) curves (Biased Judge)...")
primes_biased = select_ethical_primes(results['Biased'], importance_quantile=0.9)
Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes_biased, X_max=100, baseline='prime_theorem')
plot_Pi_B_E(
    x_vals, Pi_x, B_x, E_x,
    title="Ethical Prime Distribution (Biased Judge)",
    save_path=os.path.join(output_dir, 'paper_fig1_pi_b_e.pdf'),
    show=False
)
print(f"      Saved: {os.path.join(output_dir, 'paper_fig1_pi_b_e.pdf')}")

# Figure 2: Error growth analysis
print("\n[5/11] Figure 2: Error growth in log-log scale...")
analysis = analyze_error_growth(E_x, x_vals)
plot_error_growth(
    x_vals, E_x, analysis,
    title="Error Growth Analysis (Biased Judge)",
    save_path=os.path.join(output_dir, 'paper_fig2_error_growth.pdf'),
    show=False
)
print(f"      Saved: {os.path.join(output_dir, 'paper_fig2_error_growth.pdf')}")

# Figure 3: Multi-judge comparison
print("\n[6/11] Figure 3: Multi-judge error comparison...")
error_comparison = compare_error_distributions(results, X_max=100)
plot_multi_judge_errors(
    error_comparison,
    save_path=os.path.join(output_dir, 'paper_fig3_judge_comparison.pdf'),
    show=False
)
print(f"      Saved: {os.path.join(output_dir, 'paper_fig3_judge_comparison.pdf')}")

# Figure 4: Judge metric comparison (bar chart)
print("\n[7/11] Figure 4: Judge exponent comparison...")
plot_judge_comparison(
    comparison,
    metric='estimated_exponent',
    title='Estimated Growth Exponent α by Judge Type',
    save_path=os.path.join(output_dir, 'paper_fig4_exponent_comparison.pdf'),
    show=False
)
print(f"      Saved: {os.path.join(output_dir, 'paper_fig4_exponent_comparison.pdf')}")

# Figure 5: Spectrum analysis
print("\n[8/11] Figure 5: Frequency spectrum...")
m = build_m_sequence(primes_biased, X_max=200, mode='count')
freqs, amps = compute_spectrum(m, normalize=True)
peaks = analyze_spectrum_peaks(freqs, amps, num_peaks=5)
plot_spectrum(
    freqs, amps, peaks,
    title="Frequency Spectrum of Ethical Primes (Biased Judge)",
    save_path=os.path.join(output_dir, 'paper_fig5_spectrum.pdf'),
    show=False
)
print(f"      Saved: {os.path.join(output_dir, 'paper_fig5_spectrum.pdf')}")

# Figure 6: Zero distribution
print("\n[9/11] Figure 6: Ethical zeta function zeros...")
zeros = find_approximate_zeros(
    m,
    real_range=(0.3, 0.7),
    imag_range=(0, 30),
    grid_size=50,
    threshold=0.15
)
plot_zero_distribution(
    zeros,
    title="Ethical Zeta Function Zeros in Complex Plane",
    save_path=os.path.join(output_dir, 'paper_fig6_zeros.pdf'),
    show=False
)
print(f"      Found {len(zeros)} approximate zeros")
print(f"      Saved: {os.path.join(output_dir, 'paper_fig6_zeros.pdf')}")

# Figure 7: Complexity distribution
print("\n[10/11] Figure 7: Complexity distribution...")
plot_complexity_distribution(
    actions,
    title="Action Complexity Distribution (Zipf)",
    save_path=os.path.join(output_dir, 'paper_fig7_complexity_dist.pdf'),
    show=False
)
print(f"      Saved: {os.path.join(output_dir, 'paper_fig7_complexity_dist.pdf')}")

# Figure 8: Π(x), B(x), E(x) for Quantum Judge
if 'Quantum' in results:
    print("\n[11/11] Figure 8: Π(x), B(x), E(x) curves (Quantum Judge)...")
    primes_quantum = select_ethical_primes(results['Quantum'], importance_quantile=0.9)
    Pi_x_q, B_x_q, E_x_q, x_vals_q = compute_Pi_and_error(primes_quantum, X_max=100, baseline='prime_theorem')
    plot_Pi_B_E(
        x_vals_q, Pi_x_q, B_x_q, E_x_q,
        title="Ethical Prime Distribution (Quantum Judge)",
        save_path=os.path.join(output_dir, 'paper_fig8_quantum_judge.pdf'),
        show=False
    )
    print(f"      Saved: {os.path.join(output_dir, 'paper_fig8_quantum_judge.pdf')}")
else:
    print("\n[11/11] Figure 8: Skipped (Quantum Judge not available)")

# Generate detailed report
print("\n" + "=" * 70)
print("GENERATING REPORT")
print("=" * 70)
output_base = os.path.join(script_dir, 'output')
os.makedirs(output_base, exist_ok=True)
report_path = os.path.join(output_base, 'judge_comparison_report.md')
report = generate_report(results, output_path=report_path, format='markdown')
print(f"\nReport saved to: {report_path}")
print("\nReport preview:")
print("-" * 70)
# Handle encoding for Windows console
try:
    print(report[:1000])
except UnicodeEncodeError:
    # Fallback: print ASCII-safe version
    safe_report = report[:1000].encode('ascii', 'ignore').decode('ascii')
    print(safe_report)
print("...\n")

# Save numerical results
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("\nAll figures generated successfully!")
print("\nGenerated files:")
print(f"  - {os.path.join(output_dir, 'paper_fig1_pi_b_e.pdf')}")
print(f"  - {os.path.join(output_dir, 'paper_fig2_error_growth.pdf')}")
print(f"  - {os.path.join(output_dir, 'paper_fig3_judge_comparison.pdf')}")
print(f"  - {os.path.join(output_dir, 'paper_fig4_exponent_comparison.pdf')}")
print(f"  - {os.path.join(output_dir, 'paper_fig5_spectrum.pdf')}")
print(f"  - {os.path.join(output_dir, 'paper_fig6_zeros.pdf')}")
print(f"  - {os.path.join(output_dir, 'paper_fig7_complexity_dist.pdf')}")
if 'Quantum' in results:
    print(f"  - {os.path.join(output_dir, 'paper_fig8_quantum_judge.pdf')}")
print(f"  - {report_path}")
print("\nNext steps:")
print("  1. Review generated figures")
print("  2. Copy figures to ../figures/ for LaTeX inclusion")
print("  3. Update ethical_riemann_hypothesis.tex with results")
print("  4. Compile LaTeX paper: pdflatex ethical_riemann_hypothesis.tex")
print("\n" + "=" * 70)

# Save results to a summary file for LaTeX integration
results_summary_path = os.path.join(output_base, 'results_summary.txt')
with open(results_summary_path, 'w') as f:
    f.write("ETHICAL RIEMANN HYPOTHESIS - NUMERICAL RESULTS\n")
    f.write("=" * 70 + "\n\n")
    
    for name, metrics in comparison.items():
        if 'error' in metrics:
            continue
        
        f.write(f"{name} Judge:\n")
        f.write(f"  Total actions: {metrics['num_actions']}\n")
        f.write(f"  Ethical primes: {metrics['num_primes']}\n")
        f.write(f"  Mistake rate: {metrics['mistake_rate']:.3f}\n")
        f.write(f"  MAE: {metrics['mae']:.3f}\n")
        f.write(f"  RMSE: {metrics['rmse']:.3f}\n")
        alpha = metrics['estimated_exponent']
        within_bound = alpha <= 0.5 + 0.15
        f.write(f"  Estimated exponent: {alpha:.3f}\n")
        f.write(
            "  Within ERH-style bound (α ≲ 0.5)?: "
            f"{'Yes' if within_bound else 'No'}\n"
        )
        f.write(f"  Growth rate: {metrics['growth_rate']}\n")
        f.write(f"  R^2 (fit quality): {metrics['r_squared']:.3f}\n")
        f.write("\n")

print(f"\nNumerical results saved to: {results_summary_path}")
print("\nDone!")

