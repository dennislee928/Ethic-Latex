# README for Reviewers

This document provides essential information for reviewers evaluating this paper submission.

## Scope Note

Status date: `2026-04-12`

This reviewer guide is for the paper reproduction and research/simulation surfaces of the repository. It is not the operational guide for the separately stabilized security app path under `erh-security-app/`.

Current verified surface split:

- **Research / paper path:** `simulation/`, `erh_core/`, `erh/`, LaTeX sources, and the root SDK-style tests.
- **Verified application path:** `erh-security-app/backend` and `erh-security-app/frontend`.

## Main Paper PDF

The primary PDF is generated from the main LaTeX source:
- **Paper**: `ethical_riemann_hypothesis.pdf` (build from `ethical_riemann_hypothesis.tex` via `scripts/compile_latex.sh`)

## Reproducing Experiments

### Quick Path (Minimal Reproduction)

For reviewers with limited time, the minimal reproduction path focuses on the core experimental results:

1. **Install dependencies** (recommended: use virtual environment):
   ```bash
   bash scripts/install_dependencies.sh
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   ```
   Or: `pip install -r requirements.txt` (with an active venv).

2. **Generate main figures** (Figures 1-4):
   ```bash
   cd simulation
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   python generate_all_figures.py
   ```

3. **View key results**:
   - Check the freshly generated files under `simulation/output/`
   - Use `docs/EXPERIMENT_REPORTS.md` as the checked-in consolidated summary

### Full Reproduction Path

For complete reproduction of all experiments:

1. **Follow the quick path above**

2. **Run parameter sensitivity analysis**:
   ```bash
   cd simulation/notebooks
   jupyter notebook 04_parameter_sensitivity.ipynb
   ```

3. **Fetch and run real-data case studies**:
   ```bash
   # Fetch public datasets (Adult, UCI Student Performance, COMPAS)
   bash scripts/fetch_real_data.sh
   python scripts/convert_adult_to_csv.py
   python scripts/process_student_to_exam_cheating.py
   python scripts/generate_synthetic_sexual_abuse.py

   cd simulation/real_data
   python adult_income_case_study.py
   python exam_cheating_case_study.py
   python sexual_abuse_case_study.py
   # COMPAS: python compas_case_study.py (if data available)
   ```
   Optional: **α comparison** (real vs simulated):
   ```bash
   python scripts/calculate_alpha_comparison.py
   ```
   Outputs are generated locally under `test_report/` (for example `alpha_comparison.png`, `summary_report.md`).

4. **Run psychohistory integration tests** (if interested):
   ```bash
   bash scripts/run_psychohistory_tests.sh --quick
   ```

5. **Run quantum entanglement tests** (optional):
   ```bash
   pytest tests/test_quantum_entanglement.py -v
   ```
   Works with or without qiskit (NumPy fallback used when qiskit is unavailable).

## Supplementary Material

The following files and directories serve as the primary supplementary material bundle. Generated output directories below are reproduction outputs and may not be checked into a clean tree.

### Essential Files

1. **`docs/EXPERIMENT_REPORTS.md`**: Consolidated experiment report summarizing:
   - Judge comparison statistics
   - Numerical results summary
   - Parameter sensitivity analysis
   - Real-data case study results

2. **`simulation/output/`**: Generated output directory containing:
   - spectrum and zero analysis data
   - real-data result summaries
   - generated figures and psychohistory test outputs
   - other local reproduction artifacts created by scripts and notebooks

3. **Real-data output files under `simulation/output/`**:
   - Adult Income (UCI)
   - Exam cheating (UCI Student Performance → exam_cheating_cases.csv)
   - Sexual abuse reporting (synthetic fallback → sexual_abuse_cases.csv)
   - COMPAS (when data available)

4. **`data/`**: Fetched datasets (after `bash scripts/fetch_real_data.sh`):
   - `adult.csv`, `exam_cheating_cases.csv`, `sexual_abuse_cases.csv`, `compas-scores-two-years.csv`

5. **`test_report/`** (after running `scripts/calculate_alpha_comparison.py`): locally generated α comparison outputs, e.g. `alpha_comparison.png`, `summary_report.md`.

### Additional Material

- **`simulation/notebooks/`**: Jupyter notebooks for interactive exploration
- **`simulation/quantum/`**: Quantum oracle (optional; NumPy fallback when qiskit unavailable)
- **`simulation/adversarial.py`**: Adversarial (red-team) agent for ERH stress testing
- **`tests/PSYCHOHISTORY_TESTS_README.md`**: Documentation for psychohistory integration tests
- **`camera_ready_short/`**: Short version (8-10 pages) for workshop submissions

## Quick Review Guide

If you have limited time, focus on:

### Essential Figures
- **Figure 2** (`paper_fig2_error_growth.pdf`): Error growth analysis showing ERH-style bound comparison
- **Figure 3** (`paper_fig3_judge_comparison.pdf`): Multi-judge error comparison
- **Figure 4** (`paper_fig4_exponent_comparison.pdf`): Growth exponent comparison

### Essential Tables
- **Table 4** (in main paper): Summary of error behavior across judge types with ERH-style bound status and overall verdicts
- **Table in Section 5.5** (in main paper): Multi-seed stability metrics

### Key Sections to Review
1. **Section 4.1**: ERH definition and Remark on "necessary but not sufficient"
2. **Section 6.1**: Table 4 summary
3. **Section 6.2.x**: Individual judge results with unified terminology
4. **Section 6.6**: Real-data case study with comparison table

### Code Verification Points
- Core simulation logic: `erh_core/core/ethical_primes.py` (and re-exports in `simulation/core/`)
- Error growth analysis: `erh_core/core/ethical_primes.py` (function `analyze_error_growth`)
- Ethical zeta (vectorized): `simulation/analysis/zeta_function.py` (and `erh_core/analysis/zeta_function.py`)
- Figure generation: `simulation/generate_all_figures.py`
- Quantum judge: `simulation/quantum/simulator.py` (LocalQuantumJudge), integration in `simulation/core/judgement_system.py`
- Adversarial agent: `simulation/adversarial.py`

## Notes for Reviewers

- All experiments use fixed random seed (42) for reproducibility
- The coefficient of variation (CV) for error growth exponent α across multiple seeds is < 0.15 for all judges, indicating stable results
- The ERH-style bound terminology has been unified throughout: "Within ERH-style bound?" (Yes/No based on α ≤ 0.5) and "Near-critical ERH regime?" (whether α ≈ 0.5)
- ERH is explicitly stated as a **necessary but not sufficient** condition (see Section 4.1, Remark)

## Contact

For questions about reproducibility or supplementary material, please refer to the main repository README or open an issue at: https://github.com/dennislee928/Ethic-Latex

