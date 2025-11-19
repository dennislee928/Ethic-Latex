# Quick Start Guide

This guide will help you get started with the Ethical Riemann Hypothesis framework in 5 minutes.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Run a Simple Example

```bash
cd simulation
python run_example.py
```

This will:
1. Generate 500 moral actions with varying complexity
2. Create a BiasedJudge system
3. Evaluate all actions and identify mistakes
4. Extract "ethical primes" (critical misjudgments)
5. Test the Ethical Riemann Hypothesis

Expected output:
```
[5/5] Testing Ethical Riemann Hypothesis...

Results:
  Estimated exponent α: 0.xxx
  Expected (ERH):       0.500
  ERH satisfied:       Yes ✓ / No ✗
  Growth rate:         [category]
```

## Generate All Figures

To generate all figures for the paper:

```bash
cd simulation
python generate_all_figures.py
```

This will:
- Create 7 publication-quality figures
- Generate a detailed comparison report
- Save everything to `simulation/output/`

Takes ~2-3 minutes to run.

## Explore with Jupyter

```bash
cd simulation/notebooks
jupyter notebook
```

Start with `01_basic_simulation.ipynb` for an interactive introduction.

## Understanding Results

### ERH Satisfied (α ≈ 0.5)
✓ **Healthy judgment system**
- Errors grow slowly (like √x)
- System maintains integrity at scale
- Predictable degradation pattern

### ERH Violated (α > 0.5)
- **α ∈ (0.5, 1.0)**: Suboptimal but manageable
- **α ≈ 1.0**: Linear error growth - concerning
- **α > 1.0**: Catastrophic - errors explode with complexity

### Better than ERH (α < 0.5)
✓ **Exceptionally robust**
- Errors grow even slower than √x
- Very high-quality judgment system

## Key Files

| File | Purpose |
|------|---------|
| `simulation/run_example.py` | Quick demo (5 minutes) |
| `simulation/generate_all_figures.py` | Full paper figures (2 minutes) |
| `simulation/notebooks/01_basic_simulation.ipynb` | Interactive tutorial |
| `ethical_riemann_hypothesis.tex` | Academic paper (LaTeX) |
| `README.md` | Full documentation |

## Next Steps

1. **Quick experiment**: Modify `run_example.py` to try different judges
2. **Deep dive**: Work through the Jupyter notebooks
3. **Customize**: Create your own judgment systems
4. **Research**: Read the full paper and extend the framework

## Common Use Cases

### Compare Multiple Judges

```python
from simulation.core import generate_world
from simulation.core.judgement_system import BiasedJudge, NoisyJudge, batch_evaluate
from simulation.analysis.statistics import compare_judges

actions = generate_world(1000)
judges = {
    'Judge A': BiasedJudge(bias_strength=0.2),
    'Judge B': NoisyJudge(noise_scale=0.3)
}
results = batch_evaluate(actions, judges)
comparison = compare_judges(results)

for name, metrics in comparison.items():
    print(f"{name}: α={metrics['estimated_exponent']:.3f}, ERH={metrics['erh_satisfied']}")
```

### Analyze Your Own Judgment Function

```python
from simulation.core.judgement_system import CustomJudge

def my_judge_function(action):
    # Your custom logic here
    return action.V + some_transformation(action.c)

judge = CustomJudge(my_judge_function)
# ... then use like any other judge
```

### Export Results for Analysis

```python
from simulation.analysis.statistics import generate_report

report = generate_report(results, output_path='my_analysis.md', format='markdown')
# Also supports format='json' for programmatic access
```

## Troubleshooting

### Import errors
- Make sure you're in the `simulation/` directory when running scripts
- Or add `simulation/` to your Python path

### Figures not generating
- Check that `output/figures/` directory exists
- Ensure matplotlib backend is set correctly (use 'Agg' for non-interactive)

### Jupyter kernel issues
- Make sure Jupyter is installed: `pip install jupyter`
- Create a new kernel if needed: `python -m ipykernel install --user`

## Support

For questions or issues:
1. Check the full README.md
2. Review the LaTeX paper for theoretical background
3. Examine the source code (all modules have detailed docstrings)

## Quick Theory Refresher

**The Analogy:**
- Prime numbers ↔ Ethical primes (critical misjudgments)
- π(x) (prime count) ↔ Π(x) (ethical prime count)
- Riemann Hypothesis ↔ Ethical Riemann Hypothesis

**The Test:**
Does |E(x)| = |Π(x) - B(x)| grow like √x?

**The Meaning:**
If yes → judgment system is "healthy"
If no → systematic problems as complexity increases

---

**Ready to start?** Run:
```bash
cd simulation && python run_example.py
```

