# Quantum Simulation — Future Extensions (Beyond the Current Roadmap)

This document proposes extensions that go **beyond** the scope of
`docs/QUANTUM_SIMULATION_PLANS.md` (§1.1–§1.4, §2.1–§2.4, §3.1–§3.4). Each idea
ties back to the Ethical Riemann Hypothesis (ERH) / psychohistory program and is
paired with a concrete first-implementation sketch so an engineer can pick it up
without rediscovering the motivation.

Every section follows the same template:

- **Concept** — one-sentence pitch.
- **ERH rationale** — 2–3 sentences linking it to moral dynamics / the zeta
  structure / psychohistorical forecasting.
- **First-implementation sketch** — concrete class/function names, the
  Hamiltonian or algorithm to start with, and a single unit test to write
  first.

---

## 1. New Use Cases

### 1.1 Adversarial Moral Hamiltonian Learning (AM-HL)

- **Concept.** Train a generator/discriminator pair of parameterised Ising
  Hamiltonians where the generator proposes coupling matrices `J_ij` and the
  discriminator (a classical or hybrid network) tries to distinguish the
  resulting ground-state moral distributions from empirical ones.
- **ERH rationale.** ERH predicts that empirical moral distributions cluster on
  a low-dimensional critical line. An adversarial loss exposes *which* `J_ij`
  perturbations most strongly move the predicted distribution off the critical
  line, giving us a falsifier for the hypothesis.
- **First-implementation sketch.**
  `simulation/quantum/learning/adversarial.py` with class
  `AdversarialMoralHamiltonianLearner(num_agents, empirical_distribution)`
  exposing `.fit(epochs, lr)` and `.sample_ground_state()`. Start with a
  4-qubit chain, classical discriminator (`sklearn.LogisticRegression`), and
  VQE ground state from the existing `SocialDynamicsQuantumSimulator`. Test:
  after fitting on a synthetic Ising distribution, recovered `J_ij` should be
  within 10% of the true values on a 4-agent problem.

### 1.2 Quantum Game Theory for Moral Coalitions

- **Concept.** Embed Eisert–Wilkens–Lewenstein (EWL) quantised games into
  multi-agent coalition formation, where each moral coalition is a Bell-like
  entangled pair and defection operators are Pauli-X rotations.
- **ERH rationale.** Classical coalition stability (core, Shapley value) fails
  when agents are superposed. Quantum coalitions can sustain *non-classically
  stable* configurations that the ERH predicts around phase boundaries,
  explaining the paradox of "fragile consensus".
- **First-implementation sketch.**
  `simulation/quantum/games/quantum_coalition.py` with
  `QuantumCoalitionGame(payoff_matrix, entanglement_strength)` and method
  `.nash_equilibria()`. Start with a 2-agent Prisoner's-Dilemma-style moral
  game, parameterised by `γ ∈ [0, π/2]` entanglement. Test: at `γ = π/2` the
  equilibrium strategy is the quantum "Q" operator and yields cooperation
  payoff > classical Nash.

### 1.3 Quantum-Assisted Counterfactual Ethics

- **Concept.** Given a factual moral-state trajectory, construct a
  counterfactual by evolving the same initial state under a perturbed
  Hamiltonian, then compute the fidelity `|⟨ψ_factual(t) | ψ_cf(t)⟩|²`.
- **ERH rationale.** ERH claims moral outcomes are path-dependent yet
  bounded by zeta-line structure. Fidelity decay curves quantify how much
  "ethical work" a given counterfactual intervention does — a quantum analogue
  of the Pearl do-calculus for psychohistorical forecasting.
- **First-implementation sketch.**
  `simulation/quantum/counterfactual.py` with
  `counterfactual_fidelity(initial_state, H_factual, H_cf, times)` returning
  an array of fidelities. Reuse `scipy.linalg.expm` for small systems. Test:
  identical Hamiltonians yield fidelity ≡ 1 to within 1e-10.

### 1.4 Maxwell's-Demon Analogue for Information Asymmetry

- **Concept.** Model a public-sphere "demon" that measures a subset of agents
  and uses the classical outcomes to condition unitaries on the rest,
  extracting ordering (consensus) at the cost of measurement entropy.
- **ERH rationale.** Media, social platforms, and whistle-blowers act as
  asymmetric information channels. Quantifying the demon's work (Landauer
  bound) ties moral consensus to an actual thermodynamic cost — a principled
  substitute for the hand-waved "information pressure" term in psychohistory.
- **First-implementation sketch.**
  `simulation/quantum/thermo/moral_demon.py` with
  `MoralMaxwellDemon(n_agents, measured_subset, policy)` and
  `.run(n_steps) -> (work_extracted, entropy_produced)`. Start with a
  projective-measurement demon on a 4-qubit ring. Test: extracted work is
  bounded above by `k_B T ln 2 × measurements`.

### 1.5 Hayden–Preskill-Style Scrambling of Moral Information

- **Concept.** Inject a small "moral perturbation" into one agent and measure
  how quickly the information is scrambled across the society using the
  decoding fidelity protocol of Hayden–Preskill.
- **ERH rationale.** ERH posits that moral information is globally conserved
  but locally scrambled; scrambling time `t*` is a candidate universal
  constant across societies and maps naturally onto "half-life of a scandal".
- **First-implementation sketch.**
  `simulation/quantum/scrambling/hayden_preskill.py` with
  `scrambling_time(H, perturbation_site, threshold=0.9)`. Use random-circuit
  evolution under the existing Ising Hamiltonian and decode via the
  Yoshida–Kitaev protocol on 6–8 qubits. Test: `t*` scales as `log N` for
  fully connected `J`, `~ N` for nearest-neighbour.

### 1.6 Page-Curve Analogue for Ideology Collapse

- **Concept.** Track the Von Neumann entropy of an "ideology" subsystem as it
  is gradually re-absorbed into a larger "public" environment; expect a
  Page-curve shape peaking at half-evaporation.
- **ERH rationale.** Radical ideologies historically peak then thermalise;
  ERH+psychohistory should reproduce the Page curve of information release
  from the "evaporating" movement, connecting moral collapse to black-hole
  information theory.
- **First-implementation sketch.**
  `simulation/quantum/ideology/page_curve.py` with
  `ideology_page_curve(H_total, ideology_qubits, times)` returning
  `S(t)`. Use open-system Lindblad evolution from §3.3 once available. Test:
  curve is monotonic to peak, monotonic from peak, and symmetric within 5%.

### 1.7 Quantum Causal Inference on Policy Interventions

- **Concept.** Apply the quantum process-matrix formalism (Oreshkov–Costa–
  Brukner) to determine whether two policy interventions have a definite
  causal ordering or are in causal superposition.
- **ERH rationale.** Policy impact evaluation assumes classical causal order,
  which breaks down when multiple interventions are correlated through
  media feedback loops. A quantum causal indicator flags cases where
  classical DAG inference is unsafe for psychohistorical forecasting.
- **First-implementation sketch.**
  `simulation/quantum/causal/process_matrix.py` with
  `causal_nonseparability(W)` using the Araújo et al. witness. Start with
  the 2-policy "quantum switch" example. Test: classical-ordered input
  yields witness ≤ 0; quantum switch input yields witness > 0.

### 1.8 Quantum Voting and Quadratic-Moral Funding

- **Concept.** Cast votes as qubit rotations and tally via a parity-based
  amplitude amplification, giving a quantum analogue of quadratic voting.
- **ERH rationale.** Quadratic voting already bends the aggregation function
  towards preference *intensity*; a quantum version additionally captures
  *correlation* of preferences, aligning with ERH's non-local coupling term.
- **First-implementation sketch.**
  `simulation/quantum/voting/quantum_vote.py` with
  `QuantumQuadraticVote(n_voters, issues)` and `.tally()`. Test: for
  uncorrelated single-issue votes, the quantum tally matches classical
  quadratic voting within shot noise.

---

## 2. New Pipeline / Engineering Features

### 2.1 Tensor-Network (MPS / PEPS) Backend

- **Concept.** Swap the state-vector simulator for an MPS/PEPS backend
  (`quimb`, `ITensor`, `tensornetwork`) so societies of 50–200 agents become
  tractable.
- **ERH rationale.** Critical moral phases have bounded entanglement entropy;
  MPS exactly captures the regime ERH predicts as the "physical" one, letting
  us scale beyond the ~20-qubit state-vector ceiling.
- **First-implementation sketch.**
  `simulation/quantum/backends/mps.py` exposing an `MPSBackend` class that
  matches the existing `QuantumOracle` interface. Use `quimb.tensor` and
  start with TEBD for time evolution. Test: 10-site MPS ground energy
  matches exact diagonalisation to 1e-6.

### 2.2 GPU Simulator via cuQuantum / qsim

- **Concept.** Add an optional GPU backend using `cuquantum-python` or
  Google's `qsim`.
- **ERH rationale.** VQE parameter scans and Hamiltonian-learning epochs are
  embarrassingly parallel; a 50×-100× speed-up makes overnight hyperparameter
  sweeps of realistic moral networks feasible.
- **First-implementation sketch.**
  `simulation/quantum/backends/gpu.py` with `GPUStatevectorBackend` chosen
  via env var `ERH_QUANTUM_BACKEND=gpu`. Test: 14-qubit random circuit
  expectation values match CPU reference to 1e-10, and runtime < 2× CPU
  time on small problems (smoke test only).

### 2.3 Circuit Caching and Parameter-Shift Autodiff

- **Concept.** Cache transpiled circuits keyed on `(ansatz, topology, reps)`
  and expose a `grad(expectation, params)` helper using the parameter-shift
  rule.
- **ERH rationale.** Gradient-based Hamiltonian learning (§1.1) needs
  thousands of nearly identical circuit evaluations; caching + analytic
  gradients cuts VQE wall time by an order of magnitude.
- **First-implementation sketch.**
  `simulation/quantum/autodiff.py` with `parameter_shift_grad(circuit,
  observable, params)`, plus an LRU cache for transpiled templates. Test:
  computed gradient matches finite-difference gradient to 1e-6 on a
  2-qubit Ry-CX circuit.

### 2.4 HDF5 Trajectory-Replay Dataset Format

- **Concept.** Standardise a `.h5` schema for storing (time, density-matrix,
  observables, metadata) trajectories so experiments are reproducible.
- **ERH rationale.** Psychohistorical forecasting requires replaying and
  comparing *many* trajectories (real, counterfactual, perturbed). A stable
  dataset format decouples simulation from analysis and lets downstream
  notebooks be deterministic.
- **First-implementation sketch.**
  `simulation/quantum/io/hdf5_trajectory.py` with `save_trajectory(path,
  trajectory)` / `load_trajectory(path)`. Schema: `/rho` (T, 2^n, 2^n
  complex), `/observables` group, `/meta` attrs (`hamiltonian_hash`, `seed`,
  `timestamp`). Test: round-trip a 3-qubit 100-step trajectory and confirm
  bitwise equality.

### 2.5 Streamlit / Dash Live Dashboard

- **Concept.** A live dashboard that streams simulation state
  (energy, entropy, consensus order parameter, spread) via WebSocket.
- **ERH rationale.** Real-time monitoring is essential for long VQE runs and
  for demonstrating phase transitions to non-specialists; fits the existing
  `simulation/app.py` UI pattern.
- **First-implementation sketch.**
  `simulation/quantum/dashboard/app.py` (Streamlit) with panels for Ising
  energy, half-chain entropy, spread vs. time. Back it with a zmq PUB/SUB
  channel from the simulator. Test: a headless CI run with
  `streamlit run --server.headless true` returns 0 after 10 seconds.

### 2.6 OpenQASM 3 Export

- **Concept.** Export ERH circuits as OpenQASM 3 so they are runnable on
  IBM, IonQ, Quantinuum, and AWS Braket hardware.
- **ERH rationale.** Hardware runs are the only way to collect true noise
  signatures for §2.4 of the plan; a clean OpenQASM export is the
  prerequisite, and it also makes ERH circuits shareable as artefacts.
- **First-implementation sketch.**
  `simulation/quantum/export/qasm3.py` with `circuit_to_qasm3(qc) -> str`
  using `qiskit.qasm3.dumps`. Test: exported string is parseable by
  `qiskit.qasm3.loads` and round-trip preserves the unitary to 1e-10.

### 2.7 Benchmarking Harness vs. Classical Baselines

- **Concept.** A `pytest-benchmark` harness comparing quantum predictions to
  classical mean-field, Monte-Carlo, and agent-based baselines on the same
  moral network.
- **ERH rationale.** Without rigorous comparison we cannot claim quantum
  advantage for moral modelling; this harness turns "does quantum help?"
  into a reproducible CI metric.
- **First-implementation sketch.**
  `simulation/quantum/benchmarks/` with `bench_ising_vs_meanfield.py`,
  `bench_walk_vs_classical.py`. Test: median quantum-walk spread at
  `t = 15` is ≥ 1.5× classical spread on a 31-site line (regression check).

### 2.8 CI Fuzzing for Hamiltonian Edge Cases

- **Concept.** Use `hypothesis` to generate random interaction matrices and
  bias vectors and assert numerical invariants (hermiticity, real spectrum,
  entropy non-negativity).
- **ERH rationale.** Edge cases (fully frustrated `J`, zero bias, asymmetric
  `J`) have historically broken VQE convergence. Fuzzing catches these before
  they contaminate psychohistorical experiments.
- **First-implementation sketch.**
  `tests/quantum/test_hamiltonian_fuzz.py` with a `@given(hnp.arrays(...))`
  strategy covering sizes 2–6. Test: all generated Hamiltonians are Hermitian
  and VQE returns a finite energy.

---

## 3. New Theoretical Directions

### 3.1 SYK-Model Moral Chaos and OTOCs

- **Concept.** Replace the Ising Hamiltonian with a Sachdev–Ye–Kitaev
  Hamiltonian of random all-to-all four-fermion moral interactions and
  measure out-of-time-ordered correlators (OTOCs) as chaos diagnostics.
- **ERH rationale.** SYK saturates the Maldacena–Shenker–Stanford chaos
  bound `λ_L ≤ 2πk_B T / ℏ`. If moral systems near an ideological crisis
  saturate the same bound, that is a *universal* ERH prediction linking
  moral criticality to maximal scrambling.
- **First-implementation sketch.**
  `simulation/quantum/theory/syk_morality.py` with
  `build_syk_moral_hamiltonian(N, J, seed)` returning a sparse
  `SparsePauliOp` via Jordan–Wigner, plus `lyapunov_from_otoc(H, times)`.
  Test: measured `λ_L` on `N=8` agrees with published SYK values within
  20%.

### 3.2 Quantum Thermodynamics of Moral Work Extraction

- **Concept.** Apply the Jarzynski equality and fluctuation theorems to
  moral-state transformations driven by a time-dependent `H(t)`.
- **ERH rationale.** "Moral work" has until now been metaphorical; the
  Jarzynski framework gives it an operational, falsifiable definition
  (`⟨e^{-βW}⟩ = e^{-βΔF}`) and connects ERH free-energy landscapes to
  measurable ensemble statistics.
- **First-implementation sketch.**
  `simulation/quantum/thermo/jarzynski.py` with
  `two_point_measurement(H_protocol, beta, trajectories)` returning
  sampled work values. Test: on a Landau–Zener protocol Jarzynski equality
  holds to 3 standard deviations with 10⁴ trajectories.

### 3.3 Non-Hermitian Moral Hamiltonians with PT Symmetry

- **Concept.** Admit non-Hermitian `H` with PT symmetry to model "gain"
  (propaganda) and "loss" (censorship) channels, with exceptional points
  marking PT-symmetry breaking.
- **ERH rationale.** Classical decoherence (§3.3 of plan) only loses
  information. PT-symmetric systems allow phases where gain and loss balance
  — a natural model for resilient ideological ecosystems — and the
  exceptional point becomes a novel kind of moral phase transition.
- **First-implementation sketch.**
  `simulation/quantum/theory/pt_symmetric.py` with
  `PTHamiltonian(real_part, gamma)` and `.spectrum()`. Use dense
  diagonalisation for n ≤ 6. Test: at `gamma = 0` spectrum is real; beyond
  the critical `gamma_c` eigenvalues appear in complex conjugate pairs.

### 3.4 Holographic / AdS-CFT Analogue of Moral Boundary States

- **Concept.** Treat the society as a boundary CFT and bulk moral "fields"
  via a toy holographic code (HaPPY pentagon code).
- **ERH rationale.** ERH already posits a low-dimensional "critical line"
  governing a higher-dimensional moral manifold — this is precisely the
  holographic pattern. The HaPPY code gives an explicit, testable
  encoding of bulk (moral-deep-structure) operators into boundary
  (observed-behaviour) operators.
- **First-implementation sketch.**
  `simulation/quantum/theory/holographic.py` with
  `HappyCode(depth)` and `bulk_to_boundary(operator)` plus
  `recover_bulk(boundary_data)`. Test: bulk recovery succeeds for up to
  `floor((n-1)/2)` erasures, matching the HaPPY erasure-correction
  guarantee.

### 3.5 Measurement-Induced Phase Transitions in Belief Networks

- **Concept.** Randomly interleave unitary evolution and projective
  measurements and track the entanglement-entropy scaling to locate the
  MIPT critical point.
- **ERH rationale.** Polling, surveys, and public confessions are exactly
  projective measurements on moral states. MIPT predicts a new kind of
  critical behaviour *caused by the act of measurement*, distinct from the
  thermal criticality of §3 in the plan.
- **First-implementation sketch.**
  `simulation/quantum/theory/mipt.py` with
  `mipt_entropy_vs_p(circuit_depth, p_measure, n_qubits, shots)`. Random
  Clifford evolution + Z-basis measurements at rate `p`. Test: entropy
  follows volume law for `p < p_c` and area law for `p > p_c` on n=12.

### 3.6 Quantum Error Correction as a Metaphor for Resilient Norms

- **Concept.** Encode "core moral principles" into a logical qubit of a
  small code (surface code distance-3 or [[5,1,3]]) and measure how many
  local "moral errors" it can survive.
- **ERH rationale.** Real moral systems are surprisingly robust to local
  deviance. QEC gives a rigorous language for that robustness: logical
  moral fidelity as a function of physical error rate, with a threshold
  theorem mirroring Boyd's "moral threshold" conjecture.
- **First-implementation sketch.**
  `simulation/quantum/theory/moral_qec.py` with
  `LogicalMoralQubit(code='5_1_3')` wrapping
  `qiskit_aer.noise.NoiseModel`, and `.fidelity_vs_error_rate(rates)`.
  Test: logical fidelity exceeds physical fidelity below p ≈ 0.1.

---

## 4. Prioritisation Matrix

Ratings are 1 (lowest) to 5 (highest).

| # | Extension                                                  | Novelty | Effort | ERH Alignment |
|---|------------------------------------------------------------|:-------:|:------:|:-------------:|
| 1.1 | Adversarial moral Hamiltonian learning                    | 5 | 4 | 5 |
| 1.2 | Quantum game theory for moral coalitions                  | 4 | 3 | 4 |
| 1.3 | Quantum-assisted counterfactual ethics                    | 4 | 2 | 5 |
| 1.4 | Maxwell's-demon analogue for information asymmetry        | 4 | 3 | 4 |
| 1.5 | Hayden–Preskill scrambling of moral information           | 5 | 4 | 4 |
| 1.6 | Page-curve analogue for ideology collapse                 | 5 | 4 | 5 |
| 1.7 | Quantum causal inference on policy interventions          | 5 | 4 | 4 |
| 1.8 | Quantum voting and quadratic-moral funding                | 3 | 2 | 3 |
| 2.1 | Tensor-network (MPS/PEPS) backend                         | 3 | 4 | 4 |
| 2.2 | GPU simulator via cuQuantum / qsim                        | 2 | 3 | 3 |
| 2.3 | Circuit caching and parameter-shift autodiff              | 2 | 2 | 3 |
| 2.4 | HDF5 trajectory-replay dataset                            | 2 | 2 | 4 |
| 2.5 | Streamlit / Dash live dashboard                           | 2 | 2 | 2 |
| 2.6 | OpenQASM 3 export                                         | 2 | 1 | 3 |
| 2.7 | Benchmarking harness vs. classical baselines              | 3 | 2 | 5 |
| 2.8 | CI fuzzing for Hamiltonian edge cases                     | 2 | 1 | 3 |
| 3.1 | SYK-model moral chaos + OTOCs                             | 5 | 5 | 5 |
| 3.2 | Quantum thermodynamics of moral work                      | 4 | 3 | 5 |
| 3.3 | Non-Hermitian / PT-symmetric moral Hamiltonians           | 4 | 2 | 4 |
| 3.4 | Holographic / AdS-CFT moral boundary states               | 5 | 5 | 5 |
| 3.5 | Measurement-induced phase transitions in belief networks  | 5 | 3 | 5 |
| 3.6 | QEC as resilient-norms metaphor                           | 4 | 3 | 4 |

### Recommended ordering

A phased rollout that front-loads *high-ERH-alignment, medium-effort*
items and defers the most ambitious theoretical pieces:

1. **1.3 Counterfactual ethics** — low effort, very high ERH alignment; it
   unlocks do-calculus-style analysis immediately.
2. **2.7 Benchmarking harness** — cheap to build, but required to ground
   every later claim of quantum advantage.
3. **2.4 HDF5 trajectory dataset** — unblocks reproducible psychohistory
   experiments and is a prerequisite for 1.6 and 3.5.
4. **3.3 PT-symmetric moral Hamiltonians** — small code footprint, big
   theoretical payoff (new class of phase transitions).
5. **3.5 Measurement-induced phase transitions** — natural follow-on once
   trajectory storage and classical baselines exist.
6. **1.1 Adversarial moral Hamiltonian learning** — needs 2.3 and 2.7 to
   be practical; delivers the first end-to-end ERH falsifier.
7. **1.6 Page-curve / 1.5 Hayden–Preskill** — as a twin deliverable once
   open-system evolution (plan §3.3) is in place.
8. **3.1 SYK chaos / 3.4 Holographic code** — reserved for a dedicated
   research sprint; very high risk/reward.
9. **Engineering polish (2.1, 2.2, 2.5, 2.6, 2.8)** — schedule against
   user-facing demand; none is on the scientific critical path.

---

*Document authored by the documentation agent on 2026-04-18. It intentionally
does not duplicate any roadmap item in `docs/QUANTUM_SIMULATION_PLANS.md` or
anything already implemented under `simulation/quantum/` at the time of
writing.*
