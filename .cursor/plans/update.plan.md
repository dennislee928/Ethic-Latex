---
name: ""
overview: ""
todos: []
isProject: false
---

# Cursor Agent Execution Plan: Ethic-Latex Enhancement

## Objective

Upgrade the simulation core, optimize the CI/CD pipeline, and enhance scientific output generation.

## Skills & Tools

- **Python/Science**: `python.mdc`, `numpy.mdc`, `scipy.mdc` (for metrics)
- **Quantum**: `qiskit` (implied via python)
- **DevOps**: `github-actions.mdc`, `docker.md`
- **Frontend**: `react.mdc`, `tailwind.mdc` (for dashboard visualization)
- **Documentation**: `latex` (implied)

---

## 1. Advanced IBM Quantum Circuit Implementation

**Rationale**: The current quantum implementation is basic. For the Ethical Riemann Hypothesis simulation (modeling complex, entangled states of social consensus), upgrade to a **Variational Quantum Eigensolver (VQE) style ansatz**.

- **Parametrized rotation layers** → represent shifting ethical stances
- **Entangling layers** → represent social interactions
- **Goal** → search for "stable" ethical states

**Replace/Update `simulation/quantum/simulator.py**` with:

```python
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import EfficientSU2

class AdvancedEthicalCircuit:
    def __init__(self, n_qubits=4, entanglement='full'):
        """
        n_qubits: Number of agents/nodes in the ethical subnet.
        entanglement: 'linear', 'full', or 'circular' topology.
        """
        self.n_qubits = n_qubits
        self.simulator = AerSimulator()
        # EfficientSU2 creates a heuristic circuit often used in VQE/QML
        self.ansatz = EfficientSU2(n_qubits, reps=3, entanglement=entanglement)

    def run_social_simulation(self, parameters):
        """Run the circuit with specific ethical parameters (angles)."""
        bound_circuit = self.ansatz.assign_parameters(parameters)
        bound_circuit.measure_all()
        transpiled_qc = transpile(bound_circuit, self.simulator)
        result = self.simulator.run(transpiled_qc, shots=1024).result()
        counts = result.get_counts()
        return self._analyze_consensus(counts)

    def _analyze_consensus(self, counts):
        """Interpret |00...0> vs |11...1> as consensus states. Measures 'Ethical Stability'."""
        total_shots = sum(counts.values())
        consensus_state_0 = counts.get('0' * self.n_qubits, 0)
        consensus_state_1 = counts.get('1' * self.n_qubits, 0)
        stability_score = (consensus_state_0 + consensus_state_1) / total_shots
        return {"stability_index": stability_score, "raw_distribution": counts}
```

---

## 2. GitHub Pipeline & Output Review — Critical Analysis


| Issue            | Description                                                                                                      |
| ---------------- | -------------------------------------------c;--------------------------------------------------------------------- |
| **Critical**     | `scripts/run_simulation_batch.py` is empty → pipeline skips heavy work or runs "dry run" with no meaningful data |
| **Test Summary** | `test_summary.txt` captures stdout; if sparse, confirms simulations aren't scaling                               |
| **Workflow**     | `.github/workflows/simulation.yml` runs sequentially → inefficient for simulation projects                       |


**Improvements Required**:

- Implement the Batch Runner: populate the empty script to run parallel simulations
- Artifact Caching: cache `node_modules` and pip dependencies (currently fetches every run)
- LaTeX: use `latexmk` for reliable builds, ensuring bibliographies are generated correctly

---

## 3. Code Enhancements: Efficiency & Metrics

### 3A. Pipeline Efficiency — Parallel Batch Script

**Fill `scripts/run_simulation_batch.py**` with:

```python
# scripts/run_simulation_batch.py
import argparse
import multiprocessing
import time
import json
from simulation.core.abm_simulator import ABMSimulator  # Assuming this exists

def run_single_simulation(config):
    """Worker function for a single simulation run."""
    sim_id = config.get('id')
    print(f"Starting simulation {sim_id}...")
    sim = ABMSimulator(config)
    results = sim.run()
    output_file = f"simulation/output/sim_{sim_id}_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f)
    return f"Sim {sim_id} completed. Stability: {results.get('stability')}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--instances', type=int, default=4, help='Number of parallel instances')
    parser.add_argument('--configs', type=str, default='configs.json', help='Config file path')
    args = parser.parse_args()
    configs = [{'id': i, 'steps': 100, 'agents': 50} for i in range(10)]
    pool = multiprocessing.Pool(processes=args.instances)
    start_time = time.time()
    results = pool.map(run_single_simulation, configs)
    print(f"Batch completed in {time.time() - start_time:.2f}s")
    print("\n".join(results))

if __name__ == '__main__':
    main()
```

### 3B. Outcome Metrics — Ethical Viability Score (EVS)

**Formula**:
$$EVS = \frac{2 \cdot \text{Stability} \cdot \text{Fairness}}{\text{Stability} + \text{Fairness}} \cdot (1 - \text{Polarization})$$

**Add to `simulation/analysis/statistics.py**`:

```python
def calculate_evs(stability, fairness, polarization):
    """
    Harmonic mean of Stability and Fairness, penalized by Polarization.
    Range: [0, 1]
    """
    if stability + fairness == 0:
        return 0.0
    f1_score = 2 * (stability * fairness) / (stability + fairness)
    return f1_score * (1.0 - polarization)
```

---

## Execution Steps (Phased)

### Phase 1: Quantum Core Upgrade

1. **Refactor `simulation/quantum/simulator.py**`:
  - Replace basic circuit with `AdvancedEthicalCircuit` (EfficientSU2 ansatz).
  - Support `entanglement` options: `linear`, `full`, `circular`.
  - Add `_analyze_consensus` to compute stability from shot counts.

### Phase 2: Pipeline Repair & Optimization

1. **Fix `scripts/run_simulation_batch.py**`:
  - Implement `multiprocessing.Pool` logic (see 3A above).
  - CLI: `--instances`, `--configs`, `--output-dir`.
2. **Optimize `.github/workflows/simulation.yml**`:
  - Add `strategy.matrix` for Python 3.10 and 3.11.
  - Use `actions/cache@v3` for `~/.cache/pip` and `node_modules`.
  - Upload `simulation/output/` as build artifact.

### Phase 3: Metrics & Reporting

1. **Enhance Metrics**: Implement `calculate_evs` (see 3B); update `generate_comprehensive_report.py`.
2. **LaTeX**: Use `latexmk -pdf -interaction=nonstopmode`; add "EVS over Time" subfigure.

### Phase 4: Verification

1. Run `./scripts/run_simulation_batch.py` locally to verify core utilization.
2. Run `pytest tests/` to ensure new quantum circuit doesn't break interfaces.

