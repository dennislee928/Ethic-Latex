# Quantum Simulation Status Matrix for ERH

This document tracks the implementation and verification status of the quantum-computing roadmap for the Ethical Riemann Hypothesis (ERH) and Psychohistory stack.

## Status Summary

| Area | Status | Notes |
| --- | --- | --- |
| Plan-to-code coverage | Implemented | Most roadmap items now have concrete modules under `simulation/quantum/`. |
| CI/workflow coverage | Partial | Core simulator and integration paths are covered, but not every advanced module has dedicated tests yet. |
| Real hardware execution | Partial | IBM Runtime integration exists, but it remains smoke/manual coverage rather than full regression coverage. |
| Numerical/test stability | Partial | Entropy handling is now stable for pure states, but plotting paths still require headless execution in CI. |

## Status Legend

| Status | Meaning |
| --- | --- |
| Implemented | Feature exists in repo and is wired into import surface or runtime paths. |
| Partial | Feature exists, but test coverage, workflow coverage, or production-readiness is incomplete. |
| Planned | Feature is still roadmap-only. |
| Blocked | Feature exists conceptually, but a known defect currently limits reliable verification. |

## Roadmap Matrix

| Roadmap Item | Status | Implementation Evidence | Verification Status | Notes |
| --- | --- | --- | --- | --- |
| Large-scale entanglement of moral communities | Implemented | `simulation/quantum/entangled_communities.py`, exported via `simulation.quantum` | Partial | Dedicated module exists, but no dedicated `tests/` file covers community-network APIs yet. |
| Quantum walk for moral evolution | Implemented | `simulation/quantum/quantum_walk.py` | Partial | Code exists for line and graph walks; no dedicated workflow test currently exercises it directly. |
| QML for ERH parameter discovery | Implemented | `simulation/quantum/qml_discovery.py` | Partial | VQE-style and coupling-fit helpers exist; direct test coverage is still missing. |
| Simulating moral interference | Implemented | `simulation/quantum/interference.py` | Partial | Core functions exist; not yet represented by dedicated regression tests. |
| Qiskit / PennyLane integration layer | Implemented | `simulation/quantum/backends.py` | Partial | Abstraction exists; CI currently verifies Qiskit-oriented paths more than PennyLane-specific paths. |
| Dynamic circuit generation for psychohistory | Implemented | `simulation/quantum/dynamic_circuits.py` | Partial | Time-series compilation and execution helpers exist; dedicated tests are still needed. |
| Entanglement and discord calculators | Implemented | `simulation/quantum/entanglement_metrics.py` | Partial | Metrics exist, including `discord_proxy`; broader module-specific tests are still needed. |
| Noise models and decoherence simulation | Implemented | `simulation/quantum/noise_models.py` | Partial | Noise primitives exist; workflow coverage is indirect rather than module-specific. |
| Moral Heisenberg model | Implemented | `simulation/quantum/heisenberg.py` | Partial | Hamiltonian builders exist; direct tests are still missing. |
| Dynamic Hamiltonian evolution | Implemented | `simulation/quantum/lindblad.py`, `time_dependent_evolution` | Partial | Time-dependent evolution exists; no dedicated test file covers it yet. |
| Open quantum systems / Lindblad equation | Implemented | `simulation/quantum/lindblad.py` | Partial | Core solver exists; verification remains indirect. |
| Topological moral phases | Implemented | `simulation/quantum/topological.py` | Partial | Bloch, winding-number, and phase-classification helpers exist; direct regression tests are still missing. |
| Advanced ethical circuit / Hilbert-space engine | Implemented | `AdvancedEthicalCircuit`, `AdvancedEthicalQuantumEngine` in `simulation/quantum/simulator.py` | Partial | Covered by integration-style tests and workflow jobs; plotting must stay headless in automation. |
| Social dynamics Ising simulator | Implemented | `SocialDynamicsQuantumSimulator` in `simulation/quantum/simulator.py` | Partial | Stable targeted tests now pass in headless mode; remaining gaps are broader advanced-module coverage. |
| Hybrid psychohistory quantum integration | Implemented | `erh_core/core/hybrid_model.py` | Partial | Tested through integration paths; IBM execution is smoke/manual rather than full regression coverage. |
| Real IBM Quantum execution | Partial | `simulation/quantum/cloud.py`, IBM Runtime path in `simulation/quantum/simulator.py` and `erh_core/core/hybrid_model.py` | Partial | Available behind `IBM_QUANTUM_TOKEN`, but CI only runs a guarded smoke path and does not guarantee broad hardware regression coverage. |

## Current Workflow Coverage

| Workflow Area | Status | Scope |
| --- | --- | --- |
| Headless simulator regression | Implemented | Runs entanglement, update-plan integration, and stable Ising checks under `MPLBACKEND=Agg`. |
| NumPy fallback regression | Implemented | Confirms quantum functionality still works without Qiskit. |
| IBM Runtime smoke path | Implemented | Secret-gated smoke execution for `scripts/run_quantum_hilbert_figures.py`. |
| Full advanced-module regression | Partial | No dedicated test files yet for quantum walk, interference, topological, dynamic circuits, Lindblad, Heisenberg, or QML helpers. |

## Known Gaps

| Gap | Status | Impact | Next Action |
| --- | --- | --- | --- |
| GUI plotting dependency outside headless mode | Blocked | Local macOS runs can abort when `matplotlib` uses a GUI backend. | Keep CI on `MPLBACKEND=Agg`; optionally force a non-interactive backend in code paths that render figures. |
| Missing dedicated tests for several advanced modules | Partial | Workflow cannot honestly claim end-to-end regression coverage for the whole roadmap. | Add targeted tests for quantum walk, interference, QML, Heisenberg, Lindblad, topological, and backend-selection modules. |
| Real-hardware verification breadth | Partial | IBM workflow currently acts as smoke coverage, not comprehensive verification. | Add explicit hardware-result validation once output schema records whether a real backend was used. |

## Completion Estimate

| Dimension | Estimate |
| --- | --- |
| Feature implementation completeness | 85% |
| Verification completeness | 45% |
| Workflow completeness | 60% |
| Real-hardware readiness | 35% |
