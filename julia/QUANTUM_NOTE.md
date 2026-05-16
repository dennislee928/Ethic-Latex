# Quantum Simulation — Julia vs Python Notes

## Python files replaced by Julia (local simulation)

| Python file | Julia equivalent | What it covers |
|---|---|---|
| `simulation/quantum/simulator.py` | `julia/src/QuantumSimulator.jl` | LocalQuantumJudge, AdvancedEthicalCircuit, SocialDynamicsSimulator, MoralHamiltonian, AdvancedEthicalEngine, entropy utilities |
| `simulation/quantum/quantum_walk.py` | `julia/src/QuantumWalk.jl` | Hadamard/biased coin, shift operator, quantum walk propagation, cancel-culture spread simulation |

These two files cover **all local simulation** logic. The Julia versions use Yao.jl
for circuit construction and exact state-vector simulation via matrix algebra
(LinearAlgebra.jl), giving identical physics with no Python/Qiskit dependency.

## Python files that remain (no Julia equivalent)

| File | Reason kept |
|---|---|
| `simulation/quantum/cloud.py` | Wraps IBM Quantum Runtime (`QiskitRuntimeService`, `Sampler`). IBM's Python SDK has no Julia equivalent; real-hardware execution requires this file. |
| `simulation/quantum/worker.py` | Distributed Python worker (Celery/multiprocessing). Orchestration of cloud jobs stays in Python. |
| `simulation/quantum/interface.py` | Python abstract base class `QuantumOracle`. Used by `cloud.py` and other Python consumers; no Julia analog needed. |

## How to switch between Julia local sim and Python/Qiskit

### Use Julia local simulation (default for development/CI)

```julia
using ERH
judge = ERH.QuantumSimulator.LocalQuantumJudge(shots=1024, seed=42)
j = ERH.QuantumSimulator.judge_action(judge, 0.6)

probs, ts = ERH.QuantumWalk.quantum_walk_propagate(n_sites=31, steps=10)
```

Or run the test suite:

```bash
cd julia/
julia --project=. -e 'using Pkg; Pkg.test()'
```

### Use Python/Qiskit for local simulation

```python
from simulation.quantum.simulator import LocalQuantumJudge
judge = LocalQuantumJudge(shots=1024, seed=42)
j = judge.judge_action(0.6)
```

### Use IBM Quantum cloud (real hardware or cloud simulators)

```python
# Requires IBM_QUANTUM_TOKEN env var
from simulation.quantum.cloud import IBMQuantumBackend
backend = IBMQuantumBackend(backend_name="ibm_fez")
result = backend.run(circuit, shots=1024)
```

## Gate fidelity notes

- All Julia gates are **ideal (fidelity = 1.0)**; no noise model is applied.
- Rx(θ) with θ = difficulty × π exactly mirrors the Qiskit Rx convention.
- Bell state: H(q0) → CNOT(q0→q1) → Rx(θ_a, q0) → Rx(θ_b, q1).
- Rzz(α) implemented as CNOT · Rz(α) · CNOT (standard decomposition).
- EfficientSU2 approximated with alternating Ry + linear CNOT entanglement layers.
- TwoLocal(ry, cz) approximated with alternating Ry + CZ layers.
- Ising Hamiltonian built via explicit tensor products (no sparse encoding needed
  at n ≤ 16 qubits).
