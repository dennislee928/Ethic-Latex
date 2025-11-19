"""
Generate All Figures for the Paper

This script runs all simulations and generates publication-quality figures.
Run this before compiling the LaTeX paper to ensure all figures are up-to-date.

Usage:
    python generate_all_figures.py
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Add parent directory to path to allow imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from core.action_space import generate_world
from core.judgement_system import BiasedJudge, NoisyJudge, ConservativeJudge, RadicalJudge, batch_evaluate
from core.ethical_primes import select_ethical_primes, compute_Pi_and_error, analyze_error_growth, compare_error_distributions
from analysis.zeta_function import build_m_sequence, compute_spectrum, find_approximate_zeros, analyze_spectrum_peaks
from analysis.statistics import compare_judges, generate_report
from visualization.plots import (
    setup_paper_style, plot_Pi_B_E, plot_error_growth,
    plot_multi_judge_errors, plot_spectrum, plot_zero_distribution,
    plot_complexity_distribution, plot_judge_comparison
)

# Setup
setup_paper_style()
np.random.seed(42)

print("=" * 70)
print("ETHICAL RIEMANN HYPOTHESIS - FIGURE GENERATION")
print("=" * 70)
print()

# Ensure output directory exists
os.makedirs('output/figures', exist_ok=True)

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
    print(f"  Mistake rate: {metrics['mistake_rate']:.3f}")
    print(f"  Num primes: {metrics['num_primes']}")
    print(f"  Estimated exponent: {metrics['estimated_exponent']:.3f}")
    print(f"  ERH satisfied: {'Yes ✓' if metrics['erh_satisfied'] else 'No ✗'}")
    print(f"  Growth rate: {metrics['growth_rate']}")

print("\n" + "=" * 70)
print("GENERATING FIGURES")
print("=" * 70)

# Figure 1: Basic Π(x), B(x), E(x) for Biased Judge
print("\n[4/10] Figure 1: Π(x), B(x), E(x) curves (Biased Judge)...")
primes_biased = select_ethical_primes(results['Biased'], importance_quantile=0.9)
Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes_biased, X_max=100, baseline='prime_theorem')
plot_Pi_B_E(
    x_vals, Pi_x, B_x, E_x,
    title="Ethical Prime Distribution (Biased Judge)",
    save_path='output/figures/paper_fig1_pi_b_e.pdf',
    show=False
)
print("      Saved: output/figures/paper_fig1_pi_b_e.pdf")

# Figure 2: Error growth analysis
print("\n[5/10] Figure 2: Error growth in log-log scale...")
analysis = analyze_error_growth(E_x, x_vals)
plot_error_growth(
    x_vals, E_x, analysis,
    title="Error Growth Analysis (Biased Judge)",
    save_path='output/figures/paper_fig2_error_growth.pdf',
    show=False
)
print("      Saved: output/figures/paper_fig2_error_growth.pdf")

# Figure 3: Multi-judge comparison
print("\n[6/10] Figure 3: Multi-judge error comparison...")
error_comparison = compare_error_distributions(results, X_max=100)
plot_multi_judge_errors(
    error_comparison,
    save_path='output/figures/paper_fig3_judge_comparison.pdf',
    show=False
)
print("      Saved: output/figures/paper_fig3_judge_comparison.pdf")

# Figure 4: Judge metric comparison (bar chart)
print("\n[7/10] Figure 4: Judge exponent comparison...")
plot_judge_comparison(
    comparison,
    metric='estimated_exponent',
    title='Estimated Growth Exponent α by Judge Type',
    save_path='output/figures/paper_fig4_exponent_comparison.pdf',
    show=False
)
print("      Saved: output/figures/paper_fig4_exponent_comparison.pdf")

# Figure 5: Spectrum analysis
print("\n[8/10] Figure 5: Frequency spectrum...")
m = build_m_sequence(primes_biased, X_max=200, mode='count')
freqs, amps = compute_spectrum(m, normalize=True)
peaks = analyze_spectrum_peaks(freqs, amps, num_peaks=5)
plot_spectrum(
    freqs, amps, peaks,
    title="Frequency Spectrum of Ethical Primes (Biased Judge)",
    save_path='output/figures/paper_fig5_spectrum.pdf',
    show=False
)
print("      Saved: output/figures/paper_fig5_spectrum.pdf")

# Figure 6: Zero distribution
print("\n[9/10] Figure 6: Ethical zeta function zeros...")
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
    save_path='output/figures/paper_fig6_zeros.pdf',
    show=False
)
print(f"      Found {len(zeros)} approximate zeros")
print("      Saved: output/figures/paper_fig6_zeros.pdf")

# Figure 7: Complexity distribution
print("\n[10/10] Figure 7: Complexity distribution...")
plot_complexity_distribution(
    actions,
    title="Action Complexity Distribution (Zipf)",
    save_path='output/figures/paper_fig7_complexity_dist.pdf',
    show=False
)
print("      Saved: output/figures/paper_fig7_complexity_dist.pdf")

# Generate detailed report
print("\n" + "=" * 70)
print("GENERATING REPORT")
print("=" * 70)
report = generate_report(results, output_path='output/judge_comparison_report.md', format='markdown')
print("\nReport saved to: output/judge_comparison_report.md")
print("\nReport preview:")
print("-" * 70)
print(report[:1000])
print("...\n")

# Save numerical results
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("\nAll figures generated successfully!")
print("\nGenerated files:")
print("  - output/figures/paper_fig1_pi_b_e.pdf")
print("  - output/figures/paper_fig2_error_growth.pdf")
print("  - output/figures/paper_fig3_judge_comparison.pdf")
print("  - output/figures/paper_fig4_exponent_comparison.pdf")
print("  - output/figures/paper_fig5_spectrum.pdf")
print("  - output/figures/paper_fig6_zeros.pdf")
print("  - output/figures/paper_fig7_complexity_dist.pdf")
print("  - output/judge_comparison_report.md")
print("\nNext steps:")
print("  1. Review generated figures")
print("  2. Copy figures to ../figures/ for LaTeX inclusion")
print("  3. Update ethical_riemann_hypothesis.tex with results")
print("  4. Compile LaTeX paper: pdflatex ethical_riemann_hypothesis.tex")
print("\n" + "=" * 70)

# Save results to a summary file for LaTeX integration
with open('output/results_summary.txt', 'w') as f:
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
        f.write(f"  Estimated exponent α: {metrics['estimated_exponent']:.3f}\n")
        f.write(f"  ERH satisfied: {'Yes' if metrics['erh_satisfied'] else 'No'}\n")
        f.write(f"  Growth rate: {metrics['growth_rate']}\n")
        f.write(f"  R² (fit quality): {metrics['r_squared']:.3f}\n")
        f.write("\n")

print("\nNumerical results saved to: output/results_summary.txt")
print("\nDone!")

