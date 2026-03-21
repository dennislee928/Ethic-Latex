---
name: "ERH Phase 3: Physics-Informed Quantum & Empirical Expansion"
overview: "Upgrade ERH paper from quantum metaphor to physical evidence: Ising Hamiltonian formulation, real-data ingestion, advanced visualizations, and restructured paper with Social Physics as core mechanism."
todos:
  - id: q1
    content: "Add LaTeX Hamiltonian definition in Methodology: H = -Σ J_ij Z_i Z_j - Σ h_i X_i"
    status: pending
  - id: q2
    content: Add LaTeX notation for Z_i (Pauli-Z), J_ij (social coupling), X_i (uncertainty), h_i (external field)
    status: pending
  - id: q3
    content: "Add LaTeX text: Frustration when J_ij<0; ferromagnetic when J_ij>0"
    status: pending
  - id: q4
    content: Add LaTeX section linking Ground State to Riemann Zeta zeros (GUE statistics)
    status: pending
  - id: q5
    content: Rename construct_hamiltonian to construct_ising_hamiltonian in simulator.py
    status: pending
  - id: q6
    content: "Add algebraic sign convention: H = -Σ⟨i,j⟩ J_ij Z_i Z_j - Σ h_i X_i per user spec"
    status: pending
  - id: q7
    content: Add QAOA/VQE methods section to LaTeX Computational Model
    status: pending
  - id: q8
    content: Add magnetization (consensus) storage to hybrid_model quantum step
    status: pending
  - id: q9
    content: Implement quantum_walk module for opinion diffusion (cancel culture simulation)
    status: pending
  - id: q10
    content: Add Von Neumann entropy as echo-chamber metric in hybrid_model outputs
    status: pending
  - id: r1
    content: Create docs/QUANTUM_FORMULATION.md with full LaTeX equations
    status: pending
  - id: r2
    content: Create simulation/real_data/huggingface_loader.py
    status: pending
  - id: r3
    content: Implement text_to_interaction_matrix using sentence-transformers (all-MiniLM-L6-v2)
    status: pending
  - id: r4
    content: Add ethics_commonsense and social_i_qa dataset loading (stub if API missing)
    status: pending
  - id: r5
    content: Create simulation/real_data/aita_loader.py for Reddit r/AmItheAsshole
    status: pending
  - id: r6
    content: Implement Firecrawl integration for AITA scraping (action→judgment mapping)
    status: pending
  - id: r7
    content: Map AITA voting ratio to V(a) for empirical moral values
    status: pending
  - id: r8
    content: Create simulation/real_data/github_pr_loader.py for PR merge/reject as moral signal
    status: pending
  - id: r9
    content: Add LaTeX section 4.3 Empirical Validation Framework
    status: pending
  - id: r10
    content: Add ingestion endpoint POST /ingest/huggingface in erh-security-app
    status: pending
  - id: r11
    content: Add ingestion endpoint POST /ingest/aita (Firecrawl-based)
    status: pending
  - id: r12
    content: Add moral_stories dataset support in huggingface_loader
    status: pending
  - id: v1
    content: "Implement plot_normalized_error_growth: E(x)/sqrt(x) vs x (Riemann evidence)"
    status: pending
  - id: v2
    content: Add bounded oscillation annotation when ERH holds
    status: pending
  - id: v3
    content: "Implement plot_quantum_phase_transition: Magnetization vs h (transverse field)"
    status: pending
  - id: v4
    content: Add critical h_c marker and ordered→disordered phase labels
    status: pending
  - id: v5
    content: "Implement plot_prime_ladder: Π(x) step + Li(x) smooth overlay"
    status: pending
  - id: v6
    content: Implement plot_von_neumann_entropy_over_time
    status: pending
  - id: v7
    content: Update generate_comprehensive_report.py to call new plot functions
    status: pending
  - id: v8
    content: Save all new figures to simulation/output/figures/
    status: pending
  - id: v9
    content: Add paper_fig9_normalized_oscillation.pdf to LaTeX \IfFileExists
    status: pending
  - id: v10
    content: Add paper_fig10_phase_transition_h.pdf (transverse field diagram)
    status: pending
  - id: v11
    content: Add paper_fig11_prime_ladder.pdf to LaTeX
    status: pending
  - id: p1
    content: Add 2.2 The Quantum Isomorphism (Hamiltonian & Ising) subsection
    status: pending
  - id: p2
    content: Add 3.2 Quantum Solver Implementation (QAOA/VQE) subsection
    status: pending
  - id: p3
    content: Add 4.2 Phase Transition Analysis subsection
    status: pending
  - id: p4
    content: Add 4.3 Empirical Feasibility (real-data对接計畫) subsection
    status: pending
  - id: p5
    content: "Add Discussion: Free will vs quantum randomness"
    status: pending
  - id: p6
    content: Add Montgomery pair correlation / GUE reference in Theoretical Framework
    status: pending
  - id: i1
    content: Add unit test for construct_ising_hamiltonian sign convention
    status: pending
  - id: i2
    content: Add unit test for plot_normalized_error_growth
    status: pending
  - id: i3
    content: Add integration test for HuggingFace loader (mock path)
    status: pending
  - id: i4
    content: Update requirements.txt with datasets, sentence-transformers
    status: pending
  - id: i5
    content: Update CI workflow to generate new figures
    status: pending
isProject: true
---

# Cursor Plan: ERH Paper & Code Upgrade (Phase 3)

## Objective

Upgrade the codebase to support **Physics-Informed Quantum Simulation** (Transverse-Field Ising Model), prepare for **Real-World Data** ingestion, and generate **advanced scientific visualizations** for the LaTeX paper. Transform the quantum narrative from "metaphor" to "physical evidence" (Social Physics).

---

## Concept Overview

### 1. Quantum: From Metaphor to Physical Evidence

- **Hamiltonian definition**: $H = -\sum_{\langle i,j \rangle} J_{ij} Z_i Z_j - \sum_i h_i X_i$
- **Riemann connection**: Ground state search ↔ Zeta zeros (GUE statistics)
- **Quantum walks**: O(t) vs classical O(√t) for cancel-culture diffusion
- **Von Neumann entropy**: Echo-chamber / consensus indicator

### 2. Real Data: Empirical Validation

- HuggingFace: ethics_commonsense, social_i_qa, moral_stories
- Firecrawl: Reddit r/AmItheAsshole (YTA/NTA → V(a))
- GitHub: PR merge/reject as moral signal

### 3. Visualizations: ERH Evidence

- $E(x)/\sqrt{x}$ normalized oscillation
- Phase transition: Magnetization vs $h$
- Prime ladder: $\Pi(x)$ + $Li(x)$

### 4. Paper Structure

```text
1. Introduction
2. Theoretical Framework
   2.1 Mathematical Definition (Zeta, Primes)
   2.2 The Quantum Isomorphism (Hamiltonian & Ising)  [NEW]
3. Computational Model
   3.1 Classical Agent Logic
   3.2 Quantum Solver Implementation (QAOA/VQE)  [NEW]
4. Experiments & Results
   4.1 Synthetic Simulation
   4.2 Phase Transition Analysis  [NEW]
   4.3 Empirical Feasibility  [NEW]
5. Discussion (Free will vs quantum randomness)
```

---

## Task 1: Quantum Core Upgrade (Ising & Hamiltonian)

### LaTeX (Methodology)

Add to `ethical_riemann_hypothesis.tex` in Methodology:

```latex
We model the social moral consensus system as a \emph{Transverse-Field Ising Model}.
The total energy (Social Tension Hamiltonian) is:
$$H = -\sum_{\langle i,j \rangle} J_{ij} Z_i Z_j - \sum_{i} h_i X_i$$
where $Z_i, Z_j$ are Pauli-$Z$ operators (moral judgment: $+1$ support, $-1$ oppose),
$J_{ij}$ is social coupling ($J_{ij}>0$ ferromagnetic, $J_{ij}<0$ frustration),
$X_i$ is Pauli-$X$ (uncertainty / quantum tunneling), and $h_i$ is external field
(media pressure). Montgomery's Pair Correlation links Zeta zeros to GUE statistics;
ground-state search is structurally isomorphic to finding zeros.
```

### Python

- **Edit** `simulation/quantum/simulator.py`:
  - Ensure `construct_hamiltonian` uses convention $H = -\sum J_{ij} Z_i Z_j - \sum h_i X_i$
  - Add  `NumPyMinimumEigensolver` or `VQE` for ground state
- **Edit** `erh_core/core/hybrid_model.py`:
  - Store `system_energy` and `magnetization` in quantum results
  - Add Von Neumann entropy to outputs

---

## Task 2: Real Data Ingestion

### HuggingFace

- **Create** `simulation/real_data/huggingface_loader.py`:
  - Load `ethics_commonsense`, `social_i_qa`, `moral_stories`
  - `text_to_interaction_matrix(texts)` via sentence-transformers
  - Stub/mock when API key missing

### API

- **Update** `erh-security-app/backend/app/routers/ingestion.py`:
  - `POST /ingest/huggingface`
  - `POST /ingest/aita` (Firecrawl)

### AITA & GitHub

- **Create** `simulation/real_data/aita_loader.py`: Firecrawl → Reddit AITA
- **Create** `simulation/real_data/github_pr_loader.py`: PR merge/reject → moral signal

---

## Task 3: Advanced Visualization

- **Edit** `simulation/visualization/plots.py`:
  - `plot_normalized_error_growth`: $E(x)/\sqrt{x}$ vs $x$
  - `plot_quantum_phase_transition`: Consensus vs $h$ (transverse field)
  - `plot_prime_ladder`: $\Pi(x)$ step + $Li(x)$ smooth
  - `plot_von_neumann_entropy`: Entropy over time
- **Update** `scripts/generate_comprehensive_report.py`:
  - Call new plots and save to `simulation/output/figures/`

---

## Task 4: Paper Update Preparation

- **Create** `docs/QUANTUM_FORMULATION.md`: LaTeX equations, Ground State analogy
- **Edit** `ethical_riemann_hypothesis.tex`:
  - Add sections 2.2, 3.2, 4.2, 4.3
  - Add figure references for new plots
  - Add Discussion: free will vs quantum randomness

---

## Dependencies

- `datasets` (HuggingFace)
- `sentence-transformers` (all-MiniLM-L6-v2)
- `firecrawl` (if used)
- Existing: `qiskit`, `qiskit-aer`, `qiskit-algorithms`

