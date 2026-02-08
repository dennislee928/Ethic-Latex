"""
Quick Example: Ethical Riemann Hypothesis

A minimal example demonstrating the core concepts.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from erh_core.core.action_space import generate_world, get_action_statistics
from erh_core.core.judgement_system import BiasedJudge, evaluate_judgement
from erh_core.core.ethical_primes import select_ethical_primes, compute_Pi_and_error, analyze_error_growth

# Set seed for reproducibility
np.random.seed(42)

print("=" * 70)
print("ETHICAL RIEMANN HYPOTHESIS - QUICK EXAMPLE")
print("=" * 70)
print()

# Step 1: Generate moral action space
print("[1/5] Generating action space...")
actions = generate_world(
    num_actions=500,
    complexity_dist='zipf',
    random_seed=42
)
stats = get_action_statistics(actions)
print(f"      Created {stats['num_actions']} actions")
print(f"      Complexity range: {stats['complexity']['min']}-{stats['complexity']['max']}")

# Step 2: Create judgment system
print("\n[2/5] Creating BiasedJudge...")
judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)
print(f"      Judge: {judge}")

# Step 3: Evaluate all actions
print("\n[3/5] Evaluating actions...")
evaluate_judgement(actions, judge, tau=0.3)
stats = get_action_statistics(actions)
print(f"      Mistakes: {stats['mistakes']['count']} ({stats['mistakes']['rate']:.1%})")
print(f"      MAE: {stats['error']['mae']:.3f}")

# Step 4: Extract ethical primes
print("\n[4/5] Extracting ethical primes...")
primes = select_ethical_primes(actions, importance_quantile=0.9)
print(f"      Found {len(primes)} ethical primes")
print(f"      ({len(primes)/stats['mistakes']['count']:.1%} of all mistakes)")

# Step 5: Compute error distribution and test ERH
print("\n[5/5] Testing Ethical Riemann Hypothesis...")
Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=80)
analysis = analyze_error_growth(E_x, x_vals)

print(f"\nResults:")
print(f"  Estimated exponent α: {analysis['estimated_exponent']:.3f}")
print(f"  Expected (ERH):       0.500")
print(f"  Deviation:           {abs(analysis['estimated_exponent'] - 0.5):.3f}")
within_bound = analysis['estimated_exponent'] <= 0.5 + 0.15
print(f"  Within ERH-style bound (α ≲ 0.5)?: {'Yes' if within_bound else 'No'}")
print(
    "  Close to ERH-style target (α ≈ 0.5)?: "
    f"{'Yes' if analysis['erh_satisfied'] else 'No'}"
)
print(f"  Growth rate:         {analysis['growth_rate']}")
print(f"  R^2 (fit quality):    {analysis['r_squared']:.3f}")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

if analysis['erh_satisfied']:
    print("\n[OK] This judgment system is close to the ERH-style √x target (α ≈ 0.5).")
    print("  Errors grow on the expected √x scale, indicating 'Riemann-healthy'")
    print("  behavior in the strict sense.")
else:
    if analysis['estimated_exponent'] < 0.5:
        print("\n[OK] This system performs BETTER than the ERH-style bound predicts.")
        print("  Error growth is strictly below the √x worst-case target, i.e.,")
        print("  conservative / over-cautious rather than explosive.")
    elif analysis['estimated_exponent'] < 1.0:
        print("\n[WARNING] This system shows moderate error growth.")
        print("  Worse than the ERH-inspired bound but not catastrophic.")
    else:
        print("\n[WARNING] This system shows problematic error growth!")
        print("  Errors grow linearly or faster with complexity, indicating")
        print("  systematic degradation.")

print("\n" + "=" * 70)
print("\nFor more detailed analysis:")
print("  - Run: python generate_all_figures.py")
print("  - Or open: notebooks/01_basic_simulation.ipynb")
print()

