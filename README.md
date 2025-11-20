# Ethical Riemann Hypothesis

A mathematical framework for analyzing moral judgment errors through an analogy with the Riemann Hypothesis in number theory.

## Project Overview

This project introduces the **Ethical Riemann Hypothesis (ERH)**, which states that in a "healthy" moral judgment system, the error in predicting critical misjudgments grows at most like √x, where x is the complexity of the decision.

### Key Concepts

- **Ethical Primes**: Critical misjudgments that represent fundamental errors
- **Π(x)**: Count of ethical primes up to complexity x
- **E(x) = Π(x) - B(x)**: Error term comparing actual vs expected distribution
- **ERH**: |E(x)| ≤ C·x^(1/2 + ε) for healthy judgment systems

### Analogy with Number Theory

| Number Theory | Ethical Judgment |
|---------------|------------------|
| Prime numbers | Ethical primes (critical misjudgments) |
| π(x) | Π(x) (ethical prime count) |
| Prime Number Theorem | Baseline expectation B(x) |
| Riemann Hypothesis | Ethical Riemann Hypothesis |

## Project Structure

```
Ethic-Latex/
├── simulation/                    # Python simulation framework
│   ├── core/                     # Core modules
│   │   ├── action_space.py      # Action and world generation
│   │   ├── judgement_system.py  # Judge implementations
│   │   └── ethical_primes.py    # Prime selection and analysis
│   ├── analysis/                # Analysis tools
│   │   ├── zeta_function.py    # Ethical zeta function
│   │   └── statistics.py       # Statistical analysis
│   ├── visualization/           # Plotting utilities
│   │   └── plots.py            # All visualization functions
│   ├── notebooks/              # Jupyter notebooks
│   │   ├── 01_basic_simulation.ipynb
│   │   ├── 02_judge_comparison.ipynb
│   │   ├── 03_zeta_zeros.ipynb
│   │   ├── 04_parameter_sensitivity.ipynb
│   │   ├── 05_generate_paper_figures.ipynb
│   │   ├── 06_baseline_comparison.ipynb
│   │   └── 07_zeta_zeros_deep_analysis.ipynb
│   ├── output/                 # Generated outputs
│   │   └── figures/           # Saved figures
│   └── README.md              # Simulation documentation
├── scripts/                    # Utility scripts
│   ├── install_dependencies.*  # Dependency installation
│   ├── start_jupyter.*         # Jupyter server launcher
│   ├── compile_latex.*         # LaTeX compilation
│   └── quick-start-script/     # Quick start scripts
├── docs/                       # Documentation files
│   ├── INSTALL.md             # Installation guide
│   ├── USAGE.md               # Usage guide
│   ├── QUICKSTART.md          # Quick start guide
│   └── ...                    # Other documentation
├── tests/                      # Test files
│   ├── notebooks/             # Notebook tests (Robot Framework)
│   ├── test_streamlit_app.py  # Streamlit app test
│   └── verify_outputs.py     # Output verification
├── figures/                    # Paper figures
├── ethical_riemann_hypothesis.tex  # Main LaTeX paper
├── references.bib             # Bibliography
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```
## DEMO
<img width="1647" height="1003" alt="螢幕擷取畫面 2025-11-19 144633" src="https://github.com/user-attachments/assets/86b7e910-dc49-4d9c-ab6e-bb8dd9dceb2a" />

<img width="1732" height="994" alt="螢幕擷取畫面 2025-11-19 144430" src="https://github.com/user-attachments/assets/f883510f-b0e5-479c-a792-a93b554618be" />

<img width="1688" height="1004" alt="螢幕擷取畫面 2025-11-19 144452" src="https://github.com/user-attachments/assets/421f952c-a732-43fe-8049-6da2dba27e51" />

<img width="1026" height="574" alt="螢幕擷取畫面 2025-11-19 144748" src="https://github.com/user-attachments/assets/b1543552-036f-43b9-a35e-f058d8641683" />

## Installation

### Prerequisites

- Python 3.10 or later
- LaTeX distribution (for compiling the paper)

### Python Setup

```bash
# Clone the repository
git clone <repository-url>
cd Ethic-Latex

# Install dependencies
pip install -r requirements.txt
```

### LaTeX Setup

To compile the paper:

```bash
# Using the provided script (recommended)
bash scripts/compile_latex.sh
# or on Windows:
scripts\compile_latex.bat

# Or manually:
pdflatex ethical_riemann_hypothesis.tex
bibtex ethical_riemann_hypothesis
pdflatex ethical_riemann_hypothesis.tex
pdflatex ethical_riemann_hypothesis.tex
```

## Quick Start

### Running Basic Simulation

```python
from simulation.core import generate_world, BiasedJudge, evaluate_judgement
from simulation.core import select_ethical_primes, compute_Pi_and_error
from simulation.visualization import plot_Pi_B_E

# Generate moral action space
actions = generate_world(num_actions=1000, complexity_dist='zipf')

# Create and apply a judgment system
judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)
evaluate_judgement(actions, judge, tau=0.3)

# Extract ethical primes
primes = select_ethical_primes(actions, importance_quantile=0.9)

# Compute and plot error distribution
Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
plot_Pi_B_E(x_vals, Pi_x, B_x, E_x)
```

### Running Jupyter Notebooks

```bash
# Using the provided script (recommended)
bash scripts/start_jupyter.sh
# or on Windows:
scripts\start_jupyter.bat

# Or manually:
cd simulation/notebooks
jupyter notebook
```

Start with `01_basic_simulation.ipynb` for an introduction.

## Cloud Deployment

### Quick Deploy Options

**🚀 Streamlit Cloud (Recommended - 5 minutes)**
1. Push to GitHub
2. Visit https://share.streamlit.io
3. Connect repo → Deploy
4. Your app: `https://YOUR_APP.streamlit.app`

**📓 Binder (For Notebooks - 2 minutes)**
1. Push to GitHub
2. Visit: `https://mybinder.org/v2/gh/YOUR_USERNAME/Ethic-Latex/main`
3. Share the URL for live JupyterLab access

**🐳 Docker (Any Platform)**
```bash
docker build -t erh-app .
docker run -p 8501:8501 erh-app streamlit run simulation/app.py --server.port=8501 --server.address=0.0.0.0
```

See **[CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)** for detailed guides on:
- Streamlit Cloud, Binder, Railway, Render
- AWS, GCP, Azure
- Docker deployment
- Security considerations

## Key Results

(To be filled after running simulations)

### Judge Comparison

| Judge Type | Exponent α | ERH Satisfied | Growth Rate |
|------------|-----------|---------------|-------------|
| Biased     | TBD       | TBD           | TBD         |
| Noisy      | TBD       | TBD           | TBD         |
| Conservative| TBD      | TBD           | TBD         |
| Radical    | TBD       | TBD           | TBD         |

### Interpretation

- **α ≈ 0.5**: ERH satisfied, "Riemann-healthy" system
- **α < 0.5**: Better than ERH predicts, very robust
- **0.5 < α < 1**: Suboptimal but not catastrophic
- **α ≥ 1**: Linear or worse growth, systematic degradation

## Documentation

- **Simulation Framework**: See `simulation/README.md`
- **Installation Guide**: See `docs/INSTALL.md`
- **Usage Guide**: See `docs/USAGE.md`
- **Quick Start**: See `docs/QUICKSTART.md`
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md`
- **API Documentation**: See docstrings in individual modules
- **Theory**: See `ethical_riemann_hypothesis.tex`
- **Tutorials**: See Jupyter notebooks in `simulation/notebooks/`
- **Testing**: See `tests/README.md` for notebook testing with Robot Framework

## Applications to AI Ethics

The ERH framework provides:

1. **Quantitative Criterion**: AI systems should satisfy |E(x)| = O(√x)
2. **Bias Detection**: Violations of ERH indicate systematic failures
3. **Fairness Analysis**: Ethical primes highlight critical errors on vulnerable groups
4. **Design Guidelines**: Bounded uncertainty growth, graceful degradation

## Citation

If you use this framework in your research, please cite:

```bibtex
@article{ethical_riemann_hypothesis,
  title={The Ethical Riemann Hypothesis: A Mathematical Framework for Analyzing Moral Judgment Errors},
  author={[To be completed]},
  journal={[To be completed]},
  year={2025}
}
```

## Contributing

This is a research project. Contributions, suggestions, and discussions are welcome.

## License

MIT License

## Contact

admin@dennisleehappy.org

## Acknowledgments

This work draws inspiration from:
- The Riemann Hypothesis and analytic number theory
- AI ethics and fairness literature
- Error analysis in complex systems
- Computational social science

## Future Work

- Apply to real-world AI systems (recidivism prediction, content moderation)
- Develop theoretical proofs for ERH conditions
- Extend to multi-objective ethical frameworks
- Connect to causal inference and counterfactual reasoning
- Explore quantum computing implementations (QASM experiments)

---

**Note**: This is an exploratory research project combining pure mathematics, computational simulation, and AI ethics. The framework is meant to provoke new ways of thinking about moral judgment errors, not to replace existing ethical frameworks.

