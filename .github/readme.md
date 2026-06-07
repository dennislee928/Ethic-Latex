# Ethical Riemann Hypothesis (ERH)

- https://pypi.org/project/erh/0.1.0/
- https://www.npmjs.com/package/erh-js-sdk
- https://ethic-latex-git-feature-expensi-6e32ce-dennis-projects-5fbbc43a.vercel.app/

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Research_Preview-orange)](https://github.com/)

**A mathematical framework for analyzing moral judgment errors through an analogy with the Riemann Hypothesis in number theory.**

---

## Repository Status

Status date: `2026-04-12`

This repository still contains multiple historical and experimental surfaces. The latest stabilization work verified only the paths listed below. Treat other apps, notebooks, generated outputs, and duplicate frontends as exploratory unless they are separately revalidated.

### Currently Verified Surfaces

- `erh-security-app/backend`: FastAPI security backend with `11` passing backend tests.
- `erh-security-app/frontend`: Next.js security frontend with passing `typecheck`, `build`, and `lint`.
- `simulation/app.py`: Streamlit entrypoint imports and syntax checks pass after the `json` import fix.
- `erh`, `simulation`, `erh_core`: Root Python packages remain the canonical library surface for the research and SDK code paths.

### Architecture Map

- **Canonical core:** `erh_core/`
- **Compatibility / SDK layer:** `erh/`, `simulation/core/`, `simulation/analysis/`
- **Verified application surface:** `erh-security-app/`
- **Experimental or duplicate UI surfaces still in tree:** `frontend/`, `erh-security-app/frontend-vite/`

See [docs/SUPPORTED_SURFACES.md](docs/SUPPORTED_SURFACES.md) for the current supported-surface decision record.

## 🧭 What This Repository Can Do

This repository is both a **research artifact** (the ERH paper + simulations) and a set of **runnable tools** that apply the Ethical Riemann Hypothesis to real systems. At a glance, it can:

### 1. Model & Simulate Moral Judgment Systems
- Generate synthetic "moral action spaces" with tunable complexity distributions (`generate_world`).
- Apply pluggable judges — `BiasedJudge`, `NoisyJudge`, conservative/radical, fuzzy, and oracle-driven — to produce judgments.
- Run **Agent-Based Model (ABM)** simulations and **adversarial / red-team** stress tests against the ERH bound (`simulation/adversarial.py`, `erh_core/core/abm_simulator.py`).

### 2. Compute ERH Metrics & Diagnose "Ethical Health"
- Select **ethical primes** (critical misjudgments), compute the prime-counting function $\Pi(x)$, the baseline $B(x)$, and the error term $E(x)$.
- Fit the **error-growth exponent $\alpha$** and check the ERH boundary ($\alpha \approx 0.5$ = healthy, $\alpha \geq 1$ = systematic failure).
- Provide an **ethical zeta function**, zero analysis, statistical tests, fairness metrics, and a live **health monitor** (`E(x)` vs. Riemann bound).

### 3. Examine an LLM's Response for "Ethical Degree"
- Score model outputs through V(a) proxies — `HuggingFaceEthicalOracle` (toxicity → ethical score), `GroundTruthProxy`, and `OracleDrivenJudge` — to quantify how a model's judgments accumulate critical errors as task complexity grows.
- Surfaced to end users by the **ERH Ethics Inspector desktop app** (`desktop/`): paste LLM responses and get an ethical-degree score (0–100) + ERH health verdict, fully offline. See **[docs/DESKTOP_APP.md](docs/DESKTOP_APP.md)**.

### 4. Apply ERH to Real-World Datasets
- Built-in case studies: **Adult Income**, **COMPAS**, **Exam Cheating** (UCI Student Performance), and **Sexual Abuse** (synthetic fallback), with fetch/convert scripts.
- Empirical validation pipeline that computes real-vs-simulated $\alpha$ values.

### 5. Security Application (DevSecOps PoC)
- `erh-security-app/` — a **FastAPI backend + Next.js frontend** that ingests GitLab Merge Request / SAST data and quantifies **structural security-risk growth** using ERH metrics.

### 6. Optional Quantum & HPC Backends
- Quantum judgment oracle via `simulation/quantum/` (local simulator or IBM Quantum Runtime, with a NumPy fallback).
- A **Julia** port for performance-sensitive paths (`julia/`).

### 7. SDKs, Packaging & Publishing
- **Python SDK** (`erh`, published to PyPI) and **JavaScript/TypeScript SDK** (`js-sdk`, published to npm as `erh-js-sdk`) with a CLI.
- Reproducible builds via Docker, Binder, Streamlit Cloud, and the LaTeX paper toolchain.

### 8. Continuous Integration
- Workflows for thesis builds, simulations, quantum tests, multi-platform tests, SDK publishing, docs, and (new) **cross-platform desktop installers** (`.exe`, `.msi`, `.dmg`, `.deb`).

## 📖 Project Overview

This project introduces the **Ethical Riemann Hypothesis (ERH)**. It posits that in a "healthy" moral judgment system, the cumulative error in predicting critical misjudgments grows at most like $\sqrt{x}$, where $x$ is the complexity of the decision.

### Key Concepts

- **Ethical Primes ($P$)**: Critical misjudgments representing fundamental errors.
- **$\Pi(x)$**: The count of ethical primes up to complexity $x$.
- **$E(x) = \Pi(x) - B(x)$**: The error term comparing the actual count vs. the baseline expectation.
- **The ERH Condition**: $|E(x)| \leq C \cdot x^{1/2 + \epsilon}$ for healthy judgment systems.

### Analogy with Number Theory

| Number Theory Concept          | Ethical Judgment Analogy                            |
| :----------------------------- | :-------------------------------------------------- |
| **Prime Numbers**        | Ethical Primes (Critical Misjudgments)              |
| **$\pi(x)$**           | $\Pi(x)$ (Count of ethical primes)                |
| **Prime Number Theorem** | Baseline Expectation$B(x)$                        |
| **Riemann Hypothesis**   | Ethical Riemann Hypothesis (Bounds on error growth) |

---

## 🖼️ Demo

### macOS Desktop Demo

**[▶ Watch Demo Video (GitHub)](https://github.com/user-attachments/assets/11d00e57-6e4d-4ab7-91bc-58e05ed1da43)** | **[▶ Watch Demo Video (Mirror)](https://pub-562eb5dc8f9c4026b0afbabdb70d99a8.r2.dev/Screen%20Recording%202026-06-07%20at%205.42.12%E2%80%AFPM.mov)**

You can use the pre-release **"alpha mac app and sidecar"** to experiment.

Below are visualizations generated by the framework, showcasing the distribution of ethical primes and the behavior of the error term.

|                                            Zeta Function Analysis                                            |                                            Error Distribution                                            |
| :-----------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------: |
| ![Zeta Function Visualization](https://github.com/user-attachments/assets/86b7e910-dc49-4d9c-ab6e-bb8dd9dceb2a) | ![Error Distribution Plot](https://github.com/user-attachments/assets/f883510f-b0e5-479c-a792-a93b554618be) |

|                                     Prime Counting Function$\Pi(x)$                                     |                                          Critical Line Analysis                                          |
| :-------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------: |
| ![Prime Counting Function](https://github.com/user-attachments/assets/421f952c-a732-43fe-8049-6da2dba27e51) | ![Critical Line Analysis](https://github.com/user-attachments/assets/b1543552-036f-43b9-a35e-f058d8641683) |

---

## 📂 Project Structure

**Architecture:** `erh_core` is the Single Source of Truth for core logic. The security backend (`erh-security-app/backend`) installs the root package in editable mode (`-e ../..`) to use the latest core. `simulation` and `erh` re-export from `erh_core` when available. **V(a) proxies**: `HuggingFaceEthicalOracle` (toxicity→ethical score), `GroundTruthProxy.load_from_csv()` (empirical data), `OracleDrivenJudge` (CSV-first, Oracle fallback). **Pipeline**: `run_simulation_batch --mode judge|abm`, `run_phase_transition_exp.py`, `run_full_pipeline.sh`. Use `FULL=1 ./scripts/run_full_pipeline.sh` to include `generate_all_figures`. Verification: `python scripts/run_verification_phase4.py [--full]`.

```text
Ethic-Latex/
├── erh_core/                   # Single Source of Truth (canonical core)
│   ├── core/                   # Core modules (shared by simulation/ and erh/)
│   │   ├── action_space.py     # Action and world generation
│   │   ├── judgement_system.py # Judge implementations
│   │   └── ethical_primes.py   # Prime selection and analysis
│   └── analysis/               # Analysis tools (shared)
│       ├── erh_checks.py       # ERH bound checking
│       ├── statistics.py       # Statistical analysis
│       └── zeta_function.py    # Ethical zeta function
├── simulation/                 # Python simulation framework (research/experiments)
│   ├── models.py               # Pydantic models (Action, Judgment)
│   ├── core/                   # Re-exports from erh_core (backward compatibility)
│   ├── analysis/               # Re-exports from erh_core + simulation-specific
│   │   └── fairness_metrics.py # Simulation-specific fairness analysis
│   ├── quantum/                # Quantum oracle (optional qiskit; NumPy fallback)
│   │   ├── interface.py        # QuantumOracle interface
│   │   ├── simulator.py        # LocalQuantumJudge (local/NumPy)
│   │   └── cloud.py            # CloudQuantumJudge (IBM Quantum Runtime)
│   ├── adversarial.py          # AdversarialAgent for red-team testing
│   ├── visualization/          # Plotting utilities
│   │   └── plots.py            # All visualization functions
│   ├── notebooks/              # Jupyter notebooks for experiments
│   │   ├── 01_basic_simulation.ipynb
│   │   ├── 02_judge_comparison.ipynb
│   │   └── ... (other analysis notebooks)
│   ├── api/                    # FastAPI endpoints
│   ├── real_data/              # Real-world case studies (Adult, Exam Cheating, Sexual Abuse, COMPAS)
│   └── output/                 # Generated figures and data
├── erh/                        # Python SDK package (for distribution)
│   ├── core/                   # Re-exports from erh_core (backward compatibility)
│   ├── analysis/               # Re-exports from erh_core
│   ├── client.py               # SDK client interface
│   └── tools/                  # SDK tools and adapters
├── erh-security-app/           # Stabilized security application surface
│   ├── backend/                # FastAPI backend with regression coverage
│   ├── frontend/               # Next.js frontend (currently verified UI path)
│   └── frontend-vite/          # Alternate frontend implementation; not in the latest verified path
├── frontend/                   # Separate root Vite frontend; treat as experimental until revalidated
├── scripts/                    # Utility scripts
│   ├── fetch_real_data.sh      # Fetch Adult, COMPAS, UCI Student Performance
│   ├── convert_adult_to_csv.py # Adult → data/adult.csv
│   ├── process_student_to_exam_cheating.py  # UCI Student → data/exam_cheating_cases.csv
│   └── generate_synthetic_sexual_abuse.py   # Fallback → data/sexual_abuse_cases.csv
├── docs/                       # Documentation files
├── tests/                      # Test files
├── ethical_riemann_hypothesis.tex  # Main research paper (LaTeX)
└── requirements.txt            # Python dependencies
```

---

## ⚡ Installation

### Prerequisites

- **Python:** 3.10 or later
- **LaTeX Distribution:** (Optional, for compiling the paper)

### Python Setup

```bash
# Clone the repository
git clone <repository-url>
cd Ethic-Latex

# Recommended: use the install script (creates .venv and installs deps)
bash scripts/install_dependencies.sh
# Then: source .venv/bin/activate  (or .venv\Scripts\activate on Windows)

# Or install manually (use a virtual environment)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Optional: for quantum cloud backend, set `IBM_QUANTUM_TOKEN` in `.env` (see `.env.example`). The quantum module works without it (local/NumPy fallback).

### LaTeX Setup

To compile the research paper, you need a LaTeX distribution installed.

**macOS (Homebrew):**
```bash
# Minimal (~100MB): BasicTeX
brew install --cask basictex

# Full (~4GB): MacTeX (includes all fonts/packages)
# brew install --cask mactex
```
After installing BasicTeX, open a **new terminal** or run `eval "$(/usr/libexec/path_helper -s)"` so `pdflatex` is on PATH.

**Linux:** `sudo apt-get install texlive-full latexmk` (Ubuntu/Debian)

**Windows:** Install [MiKTeX](https://miktex.org/).

Then compile:

```bash
# Using the provided script (checks for pdflatex, prefers latexmk)
bash scripts/compile_latex.sh

# Or manually (single main file)
pdflatex ethical_riemann_hypothesis.tex
bibtex ethical_riemann_hypothesis
pdflatex ethical_riemann_hypothesis.tex
```

---

## 🚀 Quick Start

### Running a Basic Simulation

```python
from simulation.core import generate_world, BiasedJudge, evaluate_judgement
from simulation.core import select_ethical_primes, compute_Pi_and_error
from simulation.visualization import plot_Pi_B_E

# 1. Generate moral action space
actions = generate_world(num_actions=1000, complexity_dist='zipf')

# 2. Create and apply a judgment system
judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)
evaluate_judgement(actions, judge, tau=0.3)

# 3. Extract ethical primes (critical errors)
primes = select_ethical_primes(actions, importance_quantile=0.9)

# 4. Compute and plot error distribution
Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
plot_Pi_B_E(x_vals, Pi_x, B_x, E_x)
```

### Running Jupyter Notebooks

```bash
bash scripts/start_jupyter.sh
```

Start with `simulation/notebooks/01_basic_simulation.ipynb` for an introduction.

### Batch Simulation Modes

```bash
# Judge mode (default): ERH analysis with BiasedJudge, parallel instances
python scripts/run_simulation_batch.py --instances 4 --output-dir results

# ABM mode: Agent-Based Model with multiprocessing
python scripts/run_simulation_batch.py --mode abm --agents 50 --steps 100 --trials 4 --output simulation/output/batch_results.json
```

- **Judge mode**: Uses `generate_world`, `BiasedJudge`, `select_ethical_primes`, etc. Outputs per-instance JSON in `--output-dir`.
- **ABM mode**: Uses `ABMSimulator`; aggregates results to `--output` (default: `simulation/output/batch_results.json`).

### Optional: Quantum Judge and Adversarial Testing

```python
from simulation.quantum import LocalQuantumJudge
from simulation.adversarial import AdversarialAgent

# Quantum oracle (local or NumPy fallback if qiskit unavailable)
quantum_judge = LocalQuantumJudge()
# Use in place of BiasedJudge for quantum-backed judgments

# Red-team agent to stress-test ERH bound
agent = AdversarialAgent(n_actions=500)
agent.run(max_steps=100)
```

### Real-World Data (Adult, Exam Cheating, Sexual Abuse, COMPAS)

To run real-data case studies (`adult_income_case_study`, `exam_cheating_case_study`, `sexual_abuse_case_study`, `compas_case_study`), fetch and prepare datasets:

```bash
# 1. Download all datasets (Adult, COMPAS, UCI Student Performance)
bash scripts/fetch_real_data.sh

# 2. Convert and process to case-study CSV schema
python scripts/convert_adult_to_csv.py
python scripts/process_student_to_exam_cheating.py   # UCI Student Performance → exam cheating proxy
python scripts/generate_synthetic_sexual_abuse.py    # Fallback when no public case-level source
```

Expected outputs:

- `data/adult.csv` – Adult Income (from UCI adult.data/test)
- `data/exam_cheating_cases.csv` – Exam cheating proxy (from UCI Student Performance)
- `data/sexual_abuse_cases.csv` – Sexual abuse reporting (synthetic fallback)
- `data/compas-scores-two-years.csv` – COMPAS (from ProPublica GitHub)

Then run:

```bash
python -m simulation.real_data.adult_income_case_study
python -m simulation.real_data.exam_cheating_case_study
python -m simulation.real_data.sexual_abuse_case_study
python -m simulation.real_data.compas_case_study   # or run_compas_alpha
```

### Empirical Validation (COMPAS, Adult, α Values)

Run the full empirical validation pipeline to compute ERH-style α values and save results:

```bash
# Run COMPAS, Adult, and synthetic (Radical/Conservative) analyses
python scripts/run_empirical_validation.py

# Output: simulation/output/real_world_results.json
# Prints α values to stdout (e.g., COMPAS α ≈ -0.20)
```

Or use the batch runner in real-data-only mode:

```bash
python scripts/run_simulation_batch.py --real-data-only
```

**CI workflow**: The `simulation.yml` pipeline runs `run_empirical_validation.py` in the alpha-comparison job alongside `calculate_alpha_comparison.py`.

---

## ☁️ Cloud Deployment

- **🚀 Streamlit Cloud (Recommended - 5 minutes):** Push to GitHub, then deploy via the Streamlit website.
- **📓 Binder (For Notebooks - 2 minutes):** Deploy your notebooks for live access.
- **🐳 Docker (Any Platform):**

<!-- end list -->

```bash
docker build -t erh-app .
docker run -p 8501:8501 erh-app streamlit run simulation/app.py
```

See `docs/CLOUD_DEPLOYMENT.md` for detailed guides.

---

## 🔒 ERH-on-Security PoC Design Document

**Subject: Analysis of Structural Misjudgment in GitLab DevSecOps Pipelines**

This design document outlines a Proof of Concept (PoC) applying the ERH framework to quantify how systematic and fatal security misjudgments accumulate as project complexity increases within a DevSecOps pipeline.

### 1\. Objectives & Scope

| Category               | Description                                                                                                                                     |
| :--------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Core Problem** | Quantify the rate at which "truly fatal security misjudgments" (structural misjudgments) accumulate as the complexity of project changes grows. |
| **Hypothesis**   | Can we use an ERH-style metric to quantify this**Structural Risk Growth**?                                                                |
| **Scope**        | GitLab Merge Request security review pipeline (using SAST/DAST results and post-merge incident data as proxies for ground truth).               |

### 2\. Mapping ERH to Security Context

| ERH Concept                          | Security Context Mapping                                                                                                                                                                              |
| :----------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Action ($a$)**             | Defined as a**security decision event** for a single **Merge Request (MR)**.                                                                                                              |
| **Complexity ($c(a)$)**      | A composite metric of MR size and scope:$c(a) = \text{norm}(\log(1 + \text{lines\_changed}) + \lambda \cdot \text{files\_changed} + \dots)$                                                         |
| **True Value ($V(a)$)**      | **Ground Truth.** $+1$: Safe merge (no post-merge incident/unresolved high issue). $-1$: Unsafe merge (resulted in incident or high-severity issue).                                        |
| **Judgment System ($J(a)$)** | **Pipeline Judge ($J_{\text{pipe}}$):** Automated CI/SAST results. **Human Judge ($J_{\text{human}}$):** Reviewer behavior/override. **Combined Judge ($J_{\text{combo}}$).** |
| **Error ($\Delta(a)$)**      | $\Delta(a) = J(a) - V(a)$.                                                                                                                                                                          |
| **Ethical Prime ($P$)**      | A**Critical Misjudgment** ($M(a)=1$) on a **High-Importance** asset ($w(a)$ in top quantile).                                                                                         |

### 3\. Data Schema Design

#### actions (Core: MR Decisions)

| Column               | Type       | Description                              |
| :------------------- | :--------- | :--------------------------------------- |
| `action_id`        | PK (MR ID) | Unique identifier for the decision event |
| `lines_added`      | int        | Complexity factor                        |
| `files_changed`    | int        | Complexity factor                        |
| `services_touched` | string[]   | Subsystems affected (via path mapping)   |
| `merged_at`        | timestamp  | Time of merge (nullable)                 |

#### ground\_truth

| Column                 | Type          | Description                                           |
| :--------------------- | :------------ | :---------------------------------------------------- |
| `action_id`          | FK            | Link to MR                                            |
| `V`                  | float [-1, 1] | **True Value** (Post-merge security impact)     |
| `has_post\_incident` | bool          | Flag for incident discovery within observation window |
| `unresolved\_high`   | bool          | True if merged with unmitigated high/critical issues  |

#### derived\_metrics (Calculated on-the-fly or materialized)

| Column        | Type  | Description                               |
| :------------ | :---- | :---------------------------------------- |
| `action_id` | FK    | Link to MR                                |
| `c`         | float | Normalized**Complexity**            |
| `delta`     | float | $\Delta(a)$ **Error**             |
| `is_prime`  | bool  | Flag indicating an**Ethical Prime** |

### 4\. ERH Analysis Flow and Metrics

1. **Preprocessing:** Ingest GitLab API data (MRs, security reports) and calculate $c(a)$, $V(a)$, $w(a)$, $J(a)$, and prime marking for all actions.
2. **ERH-style Metrics:** Compute the following for each judge:

| Metric                            | Formula                               | Description                                               |
| :-------------------------------- | :------------------------------------ | :-------------------------------------------------------- |
| **Mistake Rate (MR)**       | $\frac{1}{N} \sum M(a)$             | Overall misjudgment frequency.                            |
| **Prime Count $\Pi(x)$**  | Count of primes where$c(a) \leq x$. | Cumulative critical error count by complexity.            |
| **Error Growth $\alpha$** | Fit$|E(x)| \sim C \cdot x^\alpha$   | Log-log linear regression to find the exponent$\alpha$. |

3. **Interpretation:** Check if $\alpha$ satisfies the ERH-style boundary. $\alpha \approx 0.5$ implies **Riemann-healthy** system with controlled risk growth. $\alpha \geq 1$ implies systematic degradation.

---

## 📈 Key Results (Expected)

The following table is a placeholder to be filled with simulation results.

| Judge Type             | Exponent$\alpha$ | ERH Satisfied? | Growth Rate Interpretation                                       |
| :--------------------- | :----------------- | :------------- | :--------------------------------------------------------------- |
| **Biased**       | TBD                | TBD            | --                                                               |
| **Noisy**        | TBD                | TBD            | --                                                               |
| **Conservative** | TBD                | TBD            | Low risk, potentially high friction ($\alpha < 0.5$)           |
| **Radical**      | TBD                | TBD            | High risk accumulation, systematic failure ($\alpha \geq 1.0$) |

---

## 📚 Documentation and Future Work

- **Simulation Framework:** See `simulation/README.md`
- **CI/Workflows:** `build_thesis_gated.yml` runs simulation → quantum tests → thesis build; `simulation.yml` fetches real data and empirical sources (HuggingFace, AITA, GitHub PR); `build_thesis.yml` fetches and processes case-study CSV before running Adult/Exam Cheating/Sexual Abuse case studies; `desktop_build.yml` builds the cross-platform desktop installers (`.exe`/`.msi`/`.dmg`/`.deb`/`.AppImage`).
- **Desktop App:** See [docs/DESKTOP_APP.md](docs/DESKTOP_APP.md) — the ERH Ethics Inspector (`desktop/`), an offline desktop tool to examine the ethical degree of LLM responses.
- **Installation Guide:** See `docs/INSTALL.md` (includes venv and optional qiskit/quantum setup)
- **Theory:** See `ethical_riemann_hypothesis.tex`
- **Tests:** `pytest tests/` (includes `test_quantum_entanglement.py`, psychohistory integration)

### Applications to AI Ethics

The ERH framework provides:

1. **Quantitative Criterion**: AI systems should satisfy $|E(x)| = O(\sqrt{x})$.
2. **Bias Detection**: Violations of ERH indicate systematic failures.
3. **Fairness Analysis**: Ethical primes highlight critical errors on vulnerable groups.

### Implemented Extensions

- **Real-world case studies:** Adult Income, Exam Cheating (UCI Student Performance), Sexual Abuse (synthetic fallback), COMPAS; `scripts/fetch_real_data.sh` fetches public sources; `scripts/process_student_to_exam_cheating.py` maps UCI data to exam-cheating schema; `scripts/calculate_alpha_comparison.py` compares real vs simulated α.
- **Quantum judgment:** Optional `simulation/quantum/` (local simulator or IBM Quantum); NumPy fallback when qiskit is unavailable.
- **Health monitor:** E(x) vs Riemann bound monitoring (see `erh-security-app` backend `/analysis/health` and frontend).
- **Adversarial agent:** `simulation/adversarial.py` for red-team testing (maximizing ethical-prime discovery).

### Future Work

- Apply the framework to more real-world AI systems (e.g., content moderation).
- Develop theoretical proofs for ERH boundary conditions.
- Explore connections to causal inference.

---

## © Citation and License

### Citation

If you use this framework in your research, please cite:

```bibtex
@article{ethical_riemann_hypothesis,
  title={The Ethical Riemann Hypothesis: A Mathematical Framework for Analyzing Moral Judgment Errors},
  author={[Author Name]},
  journal={[To be completed]},
  year={2025}
}
```

### License

This project is licensed under the **MIT License**.

### Contributing

Contributions, suggestions, and discussions are welcome.

**Contact:** admin@dennisleehappy.org
