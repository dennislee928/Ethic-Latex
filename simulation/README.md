# Ethical Riemann Hypothesis - Simulation Framework

A computational framework for modeling moral judgment errors through Riemann-inspired mathematical structures.

## Overview

This project explores the analogy between the distribution of prime numbers and the occurrence of critical moral misjudgments. Just as the Riemann Hypothesis describes the error term in prime number counting, we propose an "Ethical Riemann Hypothesis" (ERH) that characterizes the growth rate of judgment errors in moral decision systems.

## Theory

### Key Concepts

- **Action Space**: A set of actions/cases with varying complexity levels
- **True Moral Value**: V(a) ∈ ℝ, the ground truth ethical evaluation
- **Judgment**: J(a), the evaluation given by a judgment system (human/AI)
- **Error**: Δ(a) = J(a) - V(a)
- **Ethical Primes**: Critical misjudgments that cannot be reduced to simpler cases
- **Π(x)**: Count of ethical primes up to complexity x
- **B(x)**: Baseline expectation (analogous to Li(x) in number theory)
- **E(x)**: Error term E(x) = Π(x) - B(x)

### Ethical Riemann Hypothesis (ERH)

**Statement**: There exist constants C, ε > 0 such that for all x:

|E(x)| ≤ C · x^(1/2 + ε)

**Interpretation**: The cumulative deviation in critical misjudgments grows at most like √x, indicating a "healthy" judgment system where errors don't spiral out of control as complexity increases.

## Installation

```bash
pip install -r ../requirements.txt
```

## Quick Start

### Basic Simulation

```python
from simulation.core import generate_world, BiasedJudge, evaluate_judgement
from simulation.core import select_ethical_primes, compute_Pi_and_error
from simulation.visualization import plot_Pi_B_E

# Generate moral action space
actions = generate_world(num_actions=1000, complexity_dist='zipf')

# Create a judgment system
judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)

# Evaluate all actions
evaluate_judgement(actions, judge, tau=0.3)

# Extract ethical primes (critical misjudgments)
primes = select_ethical_primes(actions, importance_quantile=0.9)

# Compute error distribution
Pi_x, B_x, E_x, x_values = compute_Pi_and_error(
    primes, X_max=100, baseline='prime_theorem'
)

# Visualize
plot_Pi_B_E(x_values, Pi_x, B_x, E_x, save_path='output/figures/error_dist.pdf')
```

### Compare Multiple Judges

```python
from simulation.core import NoisyJudge, ConservativeJudge
from simulation.analysis import compare_judges
from simulation.visualization import plot_judge_comparison

judges = {
    'Biased': BiasedJudge(bias_strength=0.2),
    'Noisy': NoisyJudge(noise_scale=0.3),
    'Conservative': ConservativeJudge(threshold=0.5)
}

comparison = compare_judges(actions, judges, X_max=100)
plot_judge_comparison(comparison, save_path='output/figures/judge_comp.pdf')
```

### Spectrum Analysis

```python
from simulation.analysis import build_m_sequence, compute_spectrum
from simulation.visualization import plot_spectrum

# Build complexity distribution
m = build_m_sequence(primes, X_max=200)

# Compute Fourier spectrum
frequencies, amplitudes = compute_spectrum(m)

# Visualize frequency components
plot_spectrum(frequencies, amplitudes, save_path='output/figures/spectrum.pdf')
```

## Project Structure

```
simulation/
├── core/                   # Core modules
│   ├── action_space.py    # Action and world generation
│   ├── judgement_system.py # Judge implementations
│   └── ethical_primes.py  # Prime selection and error computation
├── analysis/              # Analysis tools
│   ├── zeta_function.py  # Zeta function and spectrum
│   └── statistics.py     # Statistical analysis
├── visualization/         # Plotting utilities
│   └── plots.py          # All visualization functions
├── notebooks/            # Jupyter notebooks
│   ├── 01_basic_simulation.ipynb
│   ├── 02_judge_comparison.ipynb
│   ├── 03_zeta_zeros.ipynb
│   ├── 04_parameter_sensitivity.ipynb
│   └── 05_generate_paper_figures.ipynb
└── output/               # Generated outputs
    └── figures/          # Saved figures
```

## Notebooks

Interactive Jupyter notebooks for exploration:

1. **01_basic_simulation.ipynb**: Introduction and basic concepts
2. **02_judge_comparison.ipynb**: Comparing different judgment systems
3. **03_zeta_zeros.ipynb**: Exploring the ethical zeta function zeros
4. **04_parameter_sensitivity.ipynb**: Parameter sensitivity analysis
5. **05_generate_paper_figures.ipynb**: Generate all paper figures

## API Documentation

### Core Classes

#### `Action`
Represents a single action/case in the moral space.
- `id`: Unique identifier
- `c`: Complexity level
- `V`: True moral value
- `w`: Importance weight
- `J`: Judgment value (assigned by judge)
- `delta`: Error Δ(a) = J(a) - V(a)
- `mistake_flag`: Binary indicator (1 if |Δ| > τ)

#### Judges
- `BiasedJudge`: Systematic bias increasing with complexity
- `NoisyJudge`: High random noise
- `ConservativeJudge`: Tends toward neutral judgments
- `RadicalJudge`: Amplifies extremes

### Key Functions

See individual module docstrings for detailed API documentation.

## Mathematical Background

This framework is inspired by:
- The Riemann Hypothesis and prime number distribution
- Error terms in analytic number theory
- Signal processing (Fourier analysis)
- AI Ethics and fairness in judgment systems

## References

1. Montgomery, H. L. (1973). The pair correlation of zeros of the zeta function
2. Granville, A., & Soundararajan, K. (2007). Large character sums
3. Jobin, A., et al. (2019). The global landscape of AI ethics guidelines
4. Mehrabi, N., et al. (2021). A survey on bias and fairness in machine learning

## License

MIT License - See LICENSE file for details

## Citation

If you use this framework in your research, please cite:

```
@article{ethical_riemann_hypothesis,
  title={The Ethical Riemann Hypothesis: A Mathematical Framework for Analyzing Moral Judgment Errors},
  author={[To be completed]},
  journal={[To be completed]},
  year={2025}
}
```

