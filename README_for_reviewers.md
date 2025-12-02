# README for Reviewers

This document provides essential information for reviewers evaluating this paper submission.

## Main Paper PDF

The primary PDF files are located at:
- **English version**: `ethical_riemann_hypothesis_en.pdf` (to be generated from `ethical_riemann_hypothesis_en.tex`)
- **Chinese version**: `ethical_riemann_hypothesis_zh.pdf` (to be generated from `ethical_riemann_hypothesis_zh.tex`)

## Reproducing Experiments

### Quick Path (Minimal Reproduction)

For reviewers with limited time, the minimal reproduction path focuses on the core experimental results:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate main figures** (Figures 1-4):
   ```bash
   cd simulation
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   python generate_all_figures.py
   ```

3. **View key results**:
   - Check `simulation/output/judge_comparison_report.md` for summary statistics
   - Check `simulation/output/results_summary.txt` for numerical results

### Full Reproduction Path

For complete reproduction of all experiments:

1. **Follow the quick path above**

2. **Run parameter sensitivity analysis**:
   ```bash
   cd simulation/notebooks
   jupyter notebook 04_parameter_sensitivity.ipynb
   ```

3. **Run real-data case studies**:
   ```bash
   cd simulation/real_data
   python adult_income_case_study.py
   ```

4. **Run psychohistory integration tests** (if interested):
   ```bash
   bash scripts/run_psychohistory_tests.sh --quick
   ```

## Supplementary Material

The following files and directories serve as the primary supplementary material bundle:

### Essential Files

1. **`docs/EXPERIMENT_REPORTS.md`**: Consolidated experiment report summarizing:
   - Judge comparison statistics
   - Numerical results summary
   - Parameter sensitivity analysis
   - Real-data case study results

2. **`simulation/output/`**: Directory containing:
   - `judge_comparison_report.md`: Detailed comparison of all judge types
   - `results_summary.txt`: Numerical summary for all judges
   - `spectrum_data.json` and `zeros_data.json`: Spectrum and zero analysis data
   - `*.csv`: Parameter sensitivity analysis results
   - `figures/`: All generated paper figures (PDF format)

3. **`simulation/output/real_data/`**: Real-data case study results:
   - Adult Income dataset analysis
   - Exam cheating case study
   - Sexual abuse reporting case study

### Additional Material

- **`simulation/notebooks/`**: Jupyter notebooks for interactive exploration
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
- Core simulation logic: `simulation/core/ethical_primes.py`
- Error growth analysis: `simulation/core/ethical_primes.py` (function `analyze_error_growth`)
- Figure generation: `simulation/generate_all_figures.py`

## Notes for Reviewers

- All experiments use fixed random seed (42) for reproducibility
- The coefficient of variation (CV) for error growth exponent α across multiple seeds is < 0.15 for all judges, indicating stable results
- The ERH-style bound terminology has been unified throughout: "Within ERH-style bound?" (Yes/No based on α ≤ 0.5) and "Near-critical ERH regime?" (whether α ≈ 0.5)
- ERH is explicitly stated as a **necessary but not sufficient** condition (see Section 4.1, Remark)

## Contact

For questions about reproducibility or supplementary material, please refer to the main repository README or open an issue at: https://github.com/dennislee928/Ethic-Latex

