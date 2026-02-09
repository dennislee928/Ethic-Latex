---
name: ""
overview: ""
todos: []
isProject: false
---

# Cursor Plan: ERH Empirical Validation & Quantum Physics Upgrade

## 🎯 Context & Objective

The "Ethical Riemann Hypothesis" (ERH) project requires a critical shift from theoretical abstraction to empirical validation and rigorous physical modeling. We must fix the "Practicality" gap by analyzing real-world datasets (COMPAS) and upgrading the quantum core to a true Ising Hamiltonian model.

## 🛠️ Required Skills

- **Quantum Physics**: Qiskit (`SparsePauliOp`), Ising Models, Hamiltonian Dynamics.
- **Data Science**: Pandas, Scipy (`curve_fit`), Numpy (complex metrics).
- **Visualization**: Matplotlib/Seaborn (Publication-quality LaTeX-style plots).
- **LaTeX**: Scientific writing, BibTeX management, Floating figure layout.

---

## 📅 Phase 1: Quantum Core "Physicalization" (Ising Model Upgrade)

*Goal: Replace the toy quantum model with a Transverse-field Ising Model ($H = -\sum J_{ij} Z_i Z_j - \sum h_i X_i$).*

- **Refactor** `simulation/quantum/simulator.py`: Remove legacy rotation-gate logic.
- **Import** `SparsePauliOp` from `qiskit.quantum_info`.
- **Implement** `calculate_coupling_coefficients(agents)`: Convert social graph weights to interaction strength $J_{ij}$.
- **Implement** `calculate_external_field(agents)`: Convert agent bias to transverse field strength $h_i$.
- **Implement** method `construct_hamiltonian(J_matrix, h_vector)` building the operator $\sum J_{ij} Z_i Z_j + \sum h_i X_i$.
- **Implement** `compute_ground_state_energy(hamiltonian)` using `NumpyMinimumEigensolver` (exact) or `VQE` (heuristic).
- **Add** `calculate_von_neumann_entropy(density_matrix)` to measure system entanglement (Echo Chamber Index).
- **Create** Unit Test: `tests/test_quantum_ising.py` to verify $H$ matrix dimensions match $2^N \times 2^N$.
- **Verify** Hamiltonian Hermitian property in tests.
- **Integrate** new simulator into `erh_core/core/hybrid_model.py` step function.
- **Store** `system_energy` and `magnetization` (consensus) in the simulation history log.

## 📅 Phase 2: Real-World Data Empirical Analysis

*Goal: Execute COMPAS/Adult simulations to get $\alpha$ values and prove ERH applicability.*

- **Audit** `simulation/real_data/compas_case_study.py`: Ensure CSV paths are correct relative to project root.
- **Implement** `load_compas_data()`: Cleanse data, handle missing values for `decile_score` and `two_year_recid`.
- **Define** Ground Truth $V(a)$: Map `two_year_recid` (0/1) to Ethical Value (-1/+1).
- **Define** Agent Judgment: Map `decile_score` (1-10) to normalized judgment (-1 to +1).
- **Define** Complexity $x$: Calculate complexity based on `priors_count` (criminal history length) + feature density.
- **Implement** `calculate_cumulative_error(data)`: Compute $E(x) = \sum (Judgment - Truth)$.
- **Implement** `fit_power_law(x, E_x)`: Use `scipy.optimize.curve_fit` to find $\alpha$ for COMPAS data.
- **Create** `simulation/real_data/adult_income_case_study.py` (if missing) mirroring the COMPAS logic.
- **Batch Execution**: Create `scripts/run_empirical_validation.py` to run both datasets and save JSON results to `simulation/output/real_world_results.json`.
- **Log Output**: Ensure the script prints the calculated $\alpha$ values to stdout for quick verification.

## 📅 Phase 3: Advanced Visualization (The "Killer Plots")

*Goal: Generate the visual evidence required to upgrade "Practicality" score to 5/5.*

- **Update** `simulation/visualization/plots.py`: Set global matplotlib style to `seaborn-paper` or `tex`.
- **Create** function `plot_compas_erh_bound(results)`:
  - Plot X: Complexity (log scale).
  - Plot Y: Cumulative Error $|E(x)|$ (log scale).
  - Overlay: Theoretical bound $y = C \cdot x^{0.5}$.
  - Overlay: Actual COMPAS error curve.
- **Create** function `plot_alpha_comparison_bar(synthetic_results, real_results)`:
  - Bar chart comparing $\alpha$ of "Radical", "Conservative", "COMPAS", "Adult".
  - Highlight COMPAS value ($\approx -0.32$).
- **Create** function `plot_quantum_phase_transition(h_values, magnetization)`:
  - Show the critical drop in consensus as external field $h$ increases.
- **Create** function `plot_normalized_error_oscillation(x, error)`:
  - Plot $E(x) / \sqrt{x}$.
  - Add horizontal lines for confidence intervals.
- **Scripting**: Update `scripts/generate_comprehensive_report.py` to call all new plot functions.
- **Output**: Ensure all plots are saved as high-res PNGs in `simulation/output/figures/`.

## 📅 Phase 4: LaTeX Manuscript Refinement

*Goal: Integrate math, results, and fix all placeholders.*

- **Open** `ethical_riemann_hypothesis.tex`.
- **Search & Replace** `[To be filled]`, `[Insert Data]`, `[Pending]` tags with actual text or "TBD" if blocked.
- **Section 4 (Methodology)**: Insert the LaTeX block for the **Ising Hamiltonian** (provided in context).
- **Section 4**: Add explanation of $Z_i$ (Judgment), $J_{ij}$ (Coupling), $h_i$ (Field).
- **Section 4**: Add paragraph connecting Ground State to Zeta Zeros (GUE Statistics).
- **Section 5 (Results)**: Rename/Add section **"5.8 Empirical Results: The COMPAS Case Study"**.
- **Section 5.8**: Paste the provided analysis text regarding COMPAS $\alpha \approx -0.32$.
- **Figures**: Update `\includegraphics` paths to point to the new "Killer Plots" generated in Phase 3.
- **Figures**: Add captions explaining "Figure X: Adherence to Riemann Bound" and "Figure Y: Structural Similarity".
- **Section 6 (Discussion)**: Add paragraph on "Quantum Random Walks" as a model for viral moral panic.
- **Section 6**: Add paragraph on "Von Neumann Entropy" as a metric for Echo Chambers.
- **Abstract**: Update abstract to mention the specific $\alpha$ values found in real-world data.

## 📅 Phase 5: Automation & CI/CD

*Goal: Ensure the pipeline runs end-to-end without manual intervention.*

- **Edit** `scripts/run_simulation_batch.py`: Ensure it accepts CLI args for `--real-data-only`.
- **Update** `.github/workflows/simulation.yml`: Add step to run `scripts/run_empirical_validation.py`.
- **Update** `.github/workflows/build_thesis.yml`: Ensure it waits for simulation artifacts before compiling LaTeX.
- **Dependency Check**: Ensure `requirements.txt` includes `scikit-learn`, `pandas`, `qiskit`, `matplotlib`.
- **Pre-commit Hook**: Create a check to ensure no `[To be filled]` strings exist in `.tex` files before committing.

## 📅 Phase 6: Final Review & Quality Assurance

- **Verify** PDF generation: Run `pdflatex` locally to check for layout breaks with new images.
- **Verify** Data integrity: Check if `simulation/output/real_world_results.json` contains non-NaN values.
- **Verify** Quantum speed: Ensure Qiskit simulation depth isn't too high for local testing (limit qubits to < 16 for testing).
- **Code Style**: Run `black` or `flake8` on new Python scripts.
- **Documentation**: Update `README.md` to explain how to run the new empirical validation scripts.
- **Self-Correction**: Review the "Conservative Judge" anomaly in the text—does the new data support or refute it? Update text accordingly.

