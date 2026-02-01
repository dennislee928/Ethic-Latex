---
name: ""
overview: ""
todos: []
isProject: false
---

# Project Plan: Ethic-Latex (ERH Framework) Enhancement & Quantum Integration

This plan outlines the steps to refactor the existing codebase, enhance the theoretical grounding with real data, and implement the Quantum Judgment extensions using Qiskit and IBM Quantum.

## Phase 1: Code Quality & Foundation Refactoring

**Goal:** Address technical debt and prepare the repo for advanced extensions.

- [x] **Dependency Management & Installation**
    - [x] Switch to a modern package manager (recommend `uv` or `poetry`) or strictly define `requirements.txt`.
    - [x] Configure `setup.py` or `pyproject.toml` to support editable installs (`pip install -e .`) to resolve import issues in tests.
    - [x] **Fix:** Refactor `tests/test_psychohistory_integration.py` to remove `sys.path.insert` hacks.

- [x] **Type Safety & Validation**
    - [x] Introduce **Pydantic** models.
    - [x] Create `simulation/models.py` (erh_core→simulation in current structure):
        - [x] Define `Action(BaseModel)` to replace the custom class.
        - [x] Define `Judgment(BaseModel)` for runtime validation of simulation data.

- [x] **Performance Optimization**
    - [x] Vectorize `ethical_zeta_product` in `simulation/analysis/zeta_function.py` (and `erh/analysis/zeta_function.py`).
    - [x] Replace the iterative product loop with `numpy` broadcasting/vectorization to support higher `max_terms` for the Riemann analogy.

## Phase 2: Scientific Grounding & Real Data

**Goal:** Anchor the "Ethical Riemann Hypothesis" in empirical reality.

- [x] **Real Data Integration**
    - [x] Expand `simulation/real_data/adult_income_case_study.py` (add `compute_real_world_alpha`).
    - [x] Implement `simulation/real_data/compas_case_study.py` and script `scripts/calculate_alpha_comparison.py` to calculate $\alpha$ for Adult Income and COMPAS datasets.
    - [x] **Output:** Generate a plot comparing Real World $\alpha$ vs. Simulated "Conservative" $\alpha$ at `simulation/output/figures/alpha_comparison_real_vs_simulated.png`.

- [x] **Complexity Metric Refinement**
    - [x] Update `erh-security-app` analysis logic.
    - [x] Implement `calculate_code_complexity(code_snippet)` in `erh-security-app/backend/app/erh_security/code_complexity.py` using **Cyclomatic Complexity** or **Halstead Complexity**.
    - [x] Use this concrete $x$ value in `compute_complexity` when `code_snippet` is provided; add `POST /analysis/complexity` endpoint.

## Phase 3: Quantum Judgment Implementation

**Goal:** Implement non-binary ethical calculations using Quantum Mechanics (Entanglement & Interference).

### 3.1 Dependencies & Configuration

- [x] Add `qiskit`, `qiskit-aer`, and `qiskit-ibm-runtime` to optional deps (pyproject.toml `[quantum]`).
- [x] Setup `.env.example` for `IBM_QUANTUM_TOKEN`.

### 3.2 Core Architecture (`simulation/quantum/`)

- [x] **Interface Definition**
    - [x] Create `simulation/quantum/__init__.py`.
    - [x] Create `simulation/quantum/interface.py`: `QuantumOracle` with `collapse_wavefunction`, `entangled_judgment`.

- [x] **Local Simulator**
    - [x] Create `simulation/quantum/simulator.py`.
    - [x] Implement `LocalQuantumJudge` using `AerSimulator`.
    - [x] Implement `rx` rotation: θ = difficulty × π.

- [x] **Cloud Backend (IBM Q)**
    - [x] Create `simulation/quantum/cloud.py`.
    - [x] Implement `CloudQuantumJudge` using `QiskitRuntimeService`.
    - [x] Implement `batch_judge` for 100+ agents.

### 3.3 Integration

- [x] Add `QuantumJudge` and `evaluate_action_quantum` in `simulation/core/judgement_system.py`.

### 3.4 Verification

- [x] Create `tests/test_quantum_entanglement.py` (Prisoner's Dilemma correlation test).

## Phase 4: Application & Visualization

**Goal:** Make the theory visible and interactive.

- [x] **Interactive Dashboard**
    - [x] Enhance `erh-security-app/frontend`.
    - [x] Create Health Monitor: `GET /analysis/health`, `HealthMonitorChart.tsx`.
    - [x] E(x) vs x^{1/2} Riemann bound; alert when violation (structural hallucination).

- [x] **Adversarial Agent**
    - [x] Create `simulation/adversarial.py`.
    - [x] Implement `AdversarialAgent` (Red Teaming) that optimizes inputs to maximize Ethical Prime discovery.