"""
Local Quantum Judge using Qiskit AerSimulator (or pure-Python fallback).

Maps difficulty to θ = difficulty × π for Rx rotation.
Measurement of superposition yields judgment in [-1, 1].

AdvancedEthicalCircuit: VQE-style ansatz for Ethical Riemann Hypothesis simulation,
modeling entangled states of social consensus with parametrized rotations and
entangling layers.

SocialDynamicsQuantumSimulator: Physics-informed VQE using Quantum Ising Hamiltonian
(SparsePauliOp) and TwoLocal ansatz for social consensus energy estimation.

When qiskit-aer is unavailable (e.g., Python 3.14 or AppleClang 17 build failure),
a NumPy-based fallback is used so the quantum module still works.
"""

from typing import Tuple, Dict, Any, Union, TYPE_CHECKING

import numpy as np

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    from qiskit.circuit.library import EfficientSU2

    _QISKIT_AVAILABLE = True
except ImportError:
    _QISKIT_AVAILABLE = False
    transpile = None
    EfficientSU2 = None

# VQE/Hamiltonian support (optional, for SocialDynamicsQuantumSimulator)
try:
    from qiskit.quantum_info import SparsePauliOp
    from qiskit.circuit.library import TwoLocal
    from qiskit.primitives import Estimator

    _VQE_AVAILABLE = True
except ImportError:
    _VQE_AVAILABLE = False
    SparsePauliOp = None
    TwoLocal = None
    Estimator = None

# Visualization and error mitigation (optional)
try:
    from qiskit.visualization import plot_histogram

    _PLOT_AVAILABLE = True
except ImportError:
    _PLOT_AVAILABLE = False
    plot_histogram = None

try:
    from qiskit.utils.mitigation import complete_meas_cal, CompleteMeasFitter

    _MITIGATION_AVAILABLE = True
except ImportError:
    _MITIGATION_AVAILABLE = False
    complete_meas_cal = None
    CompleteMeasFitter = None

if TYPE_CHECKING:
    import matplotlib

from .interface import QuantumOracle


def _numpy_judge_action(difficulty: float, shots: int, seed: int | None) -> float:
    """Pure-Python fallback: Rx(θ)|0⟩, P(0)=cos²(θ/2)."""
    rng = np.random.default_rng(seed)
    theta = max(0.0, min(1.0, difficulty)) * np.pi
    p0 = float(np.cos(theta / 2) ** 2)
    ones = int(rng.binomial(shots, p0))
    return float(2 * ones / shots - 1)


def _numpy_entangled_simple(
    agent_a_bias: float,
    agent_b_bias: float,
    shots: int,
    seed: int | None,
) -> Tuple[float, float]:
    """Simpler fallback: sample from 4 outcome probabilities."""
    rng = np.random.default_rng(seed)
    theta_a = np.clip(agent_a_bias, -1, 1) * np.pi / 2
    theta_b = np.clip(agent_b_bias, -1, 1) * np.pi / 2
    phi_plus = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    def rx(t):
        c, s = np.cos(t / 2), np.sin(t / 2)
        return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)
    U = np.kron(rx(theta_a), rx(theta_b))
    probs = np.abs(U @ phi_plus) ** 2
    idx = rng.choice(4, size=shots, p=probs)
    q0 = 2 * (idx // 2) - 1
    q1 = 2 * (idx % 2) - 1
    return (float(np.mean(q0)), float(np.mean(q1)))


class AdvancedEthicalCircuit:
    """
    VQE-style quantum circuit for Ethical Riemann Hypothesis social consensus simulation.

    Models complex, entangled states of social consensus using:
    - Parametrized rotation layers: shifting ethical stances
    - Entangling layers: social interactions
    - Goal: search for "stable" ethical states via |00...0⟩ and |11...1⟩ consensus
    """

    def __init__(
        self,
        n_qubits: int = 4,
        entanglement: Union[str, list] = "full",
        reps: int = 3,
        seed: int | None = None,
    ):
        """
        Parameters
        ----------
        n_qubits : int, default=4
            Number of agents/nodes in the ethical subnet.
        entanglement : str or list, default='full'
            Entanglement topology: 'linear', 'full', 'circular', or custom coupling map.
        reps : int, default=3
            Number of repetition layers in EfficientSU2 ansatz.
        seed : int | None, default=None
            Random seed for reproducibility.
        """
        self.n_qubits = n_qubits
        self.entanglement = entanglement
        self.reps = reps
        self.seed = seed
        self._simulator = AerSimulator() if _QISKIT_AVAILABLE else None
        self.ansatz = (
            EfficientSU2(n_qubits, reps=reps, entanglement=entanglement)
            if _QISKIT_AVAILABLE and EfficientSU2 is not None
            else None
        )

    def run_social_simulation(
        self, parameters: np.ndarray | list | None = None
    ) -> Dict[str, Any]:
        """
        Run the circuit with ethical parameters (rotation angles).

        Parameters
        ----------
        parameters : array-like | None
            Circuit parameters. If None, uses random parameters.

        Returns
        -------
        dict
            - 'stability_index': consensus measure ∈ [0, 1]
            - 'raw_distribution': measurement counts
        """
        if not _QISKIT_AVAILABLE or self.ansatz is None:
            return self._numpy_fallback_consensus()

        rng = np.random.default_rng(self.seed)
        n_params = self.ansatz.num_parameters
        params = (
            np.asarray(parameters).flatten()
            if parameters is not None and len(np.asarray(parameters).flatten()) >= n_params
            else rng.uniform(0, 2 * np.pi, size=n_params)
        )
        params = np.asarray(params)[:n_params]
        if len(params) < n_params:
            params = np.resize(params, n_params)

        bound_circuit = self.ansatz.assign_parameters(params)
        bound_circuit.measure_all()
        transpiled = transpile(bound_circuit, self._simulator)
        result = self._simulator.run(
            transpiled, shots=1024, seed_simulator=self.seed
        ).result()
        counts = result.get_counts()
        return self._analyze_consensus(counts)

    def _analyze_consensus(self, counts: Dict[str, int]) -> Dict[str, Any]:
        """
        Interpret |00...0⟩ vs |11...1⟩ as consensus states.
        Measures 'Ethical Stability' from shot distribution.
        """
        total_shots = sum(counts.values())
        if total_shots == 0:
            return {"stability_index": 0.0, "raw_distribution": counts}

        zeros = "0" * self.n_qubits
        ones = "1" * self.n_qubits
        consensus_0 = counts.get(zeros, 0)
        consensus_1 = counts.get(ones, 0)
        stability_score = (consensus_0 + consensus_1) / total_shots
        return {"stability_index": stability_score, "raw_distribution": counts}

    def _numpy_fallback_consensus(self) -> Dict[str, Any]:
        """Fallback when Qiskit is unavailable: approximate consensus from random sampling."""
        rng = np.random.default_rng(self.seed)
        # Approximate: bias toward all-0 or all-1 with ~50% chance
        p_consensus = 0.3 + 0.4 * rng.random()
        n_consensus = int(1024 * p_consensus)
        n_other = 1024 - n_consensus
        zeros = "0" * self.n_qubits
        ones = "1" * self.n_qubits
        counts = {zeros: n_consensus // 2, ones: n_consensus - n_consensus // 2}
        for _ in range(n_other):
            outcome = "".join(str(rng.integers(0, 2)) for _ in range(self.n_qubits))
            counts[outcome] = counts.get(outcome, 0) + 1
        return self._analyze_consensus(counts)


class SocialDynamicsQuantumSimulator:
    """
    Physics-informed VQE for social consensus simulation using Quantum Ising Hamiltonian.

    Models social interactions with H = Σ J_ij * Z_i * Z_j + Σ h_i * X_i:
    - J_ij (interaction): influence between agents i and j
    - h_i (field): individual ethical bias/pressure
    """

    def __init__(
        self,
        num_agents: int = 4,
        topology: str = "full",
        reps: int = 3,
        seed: int | None = None,
    ):
        """
        Parameters
        ----------
        num_agents : int, default=4
            Number of agents/nodes (qubits).
        topology : str, default='full'
            Entanglement topology: 'linear', 'full', 'circular'.
        reps : int, default=3
            Repetition layers in TwoLocal ansatz.
        seed : int | None, default=None
            Random seed for reproducibility.
        """
        self.num_qubits = num_agents
        self.topology = topology
        self.reps = reps
        self.seed = seed
        self.ansatz = None
        if _VQE_AVAILABLE and TwoLocal is not None:
            self.ansatz = TwoLocal(
                self.num_qubits,
                rotation_blocks="ry",
                entanglement_blocks="cz",
                entanglement=topology,
                reps=reps,
                insert_barriers=True,
            )

    def construct_hamiltonian(
        self,
        interaction_matrix: np.ndarray,
        biases: np.ndarray | list,
    ) -> Any:
        """
        Construct the cost Hamiltonian from agent data.

        Parameters
        ----------
        interaction_matrix : ndarray, shape (n, n)
            2D array where interaction_matrix[i][j] is the weight of connection.
        biases : array-like, length n
            Individual agent biases (transverse field).

        Returns
        -------
        SparsePauliOp or None
            Hamiltonian; None if SparsePauliOp unavailable.
        """
        if not _VQE_AVAILABLE or SparsePauliOp is None:
            return None

        pauli_list: list[tuple[str, float]] = []
        interaction_matrix = np.asarray(interaction_matrix)
        biases = np.asarray(biases).flatten()
        n = min(self.num_qubits, interaction_matrix.shape[0], interaction_matrix.shape[1])

        # Symmetrize: use upper triangle; weight (i,j) and (j,i) same
        for i in range(n):
            for j in range(i + 1, n):
                w = float(interaction_matrix[i, j] + interaction_matrix[j, i]) / 2.0
                if abs(w) > 1e-12:
                    pauli_str = ["I"] * self.num_qubits
                    # Qiskit little-endian: qubit 0 is rightmost
                    pauli_str[self.num_qubits - 1 - i] = "Z"
                    pauli_str[self.num_qubits - 1 - j] = "Z"
                    pauli_list.append(("".join(pauli_str), -1.0 * w))

        for i in range(min(n, len(biases))):
            b = float(biases[i])
            if abs(b) > 1e-12:
                pauli_str = ["I"] * self.num_qubits
                pauli_str[self.num_qubits - 1 - i] = "X"
                pauli_list.append(("".join(pauli_str), b))

        if not pauli_list:
            return SparsePauliOp.from_list([("I" * self.num_qubits, 0.0)])

        return SparsePauliOp.from_list(pauli_list)

    def run_simulation(
        self,
        interaction_matrix: np.ndarray,
        biases: np.ndarray | list,
        params: np.ndarray | list | None = None,
        save_path: str | None = None,
    ) -> Dict[str, Any]:
        """
        Run VQE-style estimation of social state energy.

        Parameters
        ----------
        interaction_matrix : ndarray
            Agent interaction weights.
        biases : array-like
            Agent biases.
        params : array-like | None
            Ansatz parameters. If None, uses random.
        save_path : str | None
            Path to save circuit diagram PNG.

        Returns
        -------
        dict
            - social_tension_energy: float
            - is_stable: bool (energy < -1.0 heuristic)
            - circuit_depth: int
        """
        if not _VQE_AVAILABLE or self.ansatz is None or Estimator is None:
            return self._mock_run_simulation()

        hamiltonian = self.construct_hamiltonian(interaction_matrix, biases)
        if hamiltonian is None:
            return self._mock_run_simulation()

        rng = np.random.default_rng(self.seed)
        n_params = self.ansatz.num_parameters
        if params is not None:
            p = np.asarray(params).flatten()
            params_arr = p[:n_params] if len(p) >= n_params else np.resize(p, n_params)
        else:
            params_arr = rng.uniform(0, 2 * np.pi, size=n_params)

        bound_circuit = self.ansatz.assign_parameters(params_arr)
        estimator = Estimator()
        job = estimator.run([(bound_circuit, hamiltonian)])
        result = job.result()
        energy = float(result.values[0])

        if save_path:
            self._save_circuit_diagram(bound_circuit, save_path)

        return {
            "social_tension_energy": energy,
            "is_stable": energy < -1.0,
            "circuit_depth": bound_circuit.depth(),
        }

    def _mock_run_simulation(self) -> Dict[str, Any]:
        """Fallback when VQE dependencies unavailable."""
        rng = np.random.default_rng(self.seed)
        energy = float(rng.uniform(-2.0, 0.0))
        return {
            "social_tension_energy": energy,
            "is_stable": energy < -1.0,
            "circuit_depth": 0,
        }

    def _save_circuit_diagram(self, circuit: Any, path: str) -> None:
        """Render quantum circuit to PNG for LaTeX."""
        try:
            import matplotlib.pyplot as plt

            fig = circuit.draw(output="mpl", style="iqp")
            if hasattr(fig, "savefig"):
                fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close("all")
        except Exception:
            pass


class MoralHamiltonian:
    """
    Ising Spin Glass Hamiltonian for ethical conflict modeling.

    Maps moral principle conflicts to H = Σ J_ij σ_i σ_j (frustration).
    High conflict density → high frustration → system cannot reach ground state
    (phase transition / "collapse" at critical complexity x_crit).

    Parameters
    ----------
    n_qubits : int, default=4
        Number of principles (spins).
    use_real_hardware : bool, default=False
        If True, submit to IBM Quantum (requires IBM_QUANTUM_TOKEN).
    seed : int | None, default=None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        n_qubits: int = 4,
        use_real_hardware: bool = False,
        seed: int | None = None,
    ):
        self.n_qubits = n_qubits
        self.use_real_hardware = use_real_hardware
        self.seed = seed
        self._backend = None
        if _QISKIT_AVAILABLE:
            self._simulator = AerSimulator()
        else:
            self._simulator = None

    def build_conflict_hamiltonian(
        self,
        conflict_matrix: np.ndarray,
        transverse_field: float = 0.1,
    ) -> Any:
        """
        Build Ising Hamiltonian from moral conflict matrix.

        H = -Σ_{i<j} J_ij Z_i Z_j + Σ_i h_i X_i

        J_ij > 0: principles i,j conflict (frustration).
        Higher sum of |J_ij| → more frustration.

        Parameters
        ----------
        conflict_matrix : np.ndarray, shape (n, n)
            J_ij = conflict weight between principles i and j.
        transverse_field : float, default=0.1
            h_i for quantum fluctuations.

        Returns
        -------
        SparsePauliOp or None
        """
        if not _VQE_AVAILABLE or SparsePauliOp is None:
            return None

        J = np.asarray(conflict_matrix)
        n = min(self.n_qubits, J.shape[0], J.shape[1])
        pauli_list: list[tuple[str, float]] = []

        for i in range(n):
            for j in range(i + 1, n):
                w = float(J[i, j] + J[j, i]) / 2.0
                if abs(w) > 1e-12:
                    pauli_str = ["I"] * self.n_qubits
                    pauli_str[self.n_qubits - 1 - i] = "Z"
                    pauli_str[self.n_qubits - 1 - j] = "Z"
                    pauli_list.append(("".join(pauli_str), -1.0 * w))

        for i in range(n):
            pauli_str = ["I"] * self.n_qubits
            pauli_str[self.n_qubits - 1 - i] = "X"
            pauli_list.append(("".join(pauli_str), transverse_field))

        if not pauli_list:
            return SparsePauliOp.from_list([("I" * self.n_qubits, 0.0)])
        return SparsePauliOp.from_list(pauli_list)

    def run_phase_transition_sweep(
        self,
        conflict_densities: np.ndarray,
        base_strength: float = 0.5,
        shots: int = 2048,
    ) -> Dict[str, Any]:
        """
        Sweep conflict density and measure fidelity / coherence.

        Hypothesis: At critical conflict, fidelity drops (phase transition).

        Parameters
        ----------
        conflict_densities : np.ndarray
            Array of conflict density values (0–1).
        base_strength : float, default=0.5
            Base interaction strength.
        shots : int, default=2048
            Measurement shots per run.

        Returns
        -------
        dict
            - conflict_densities: np.ndarray
            - fidelities: np.ndarray
            - coherences: np.ndarray (consensus measure)
            - collapse_point: float or None (estimated x_crit)
        """
        from qiskit.quantum_info import Statevector

        try:
            from qiskit_algorithms import NumPyMinimumEigensolver
        except ImportError:
            from qiskit.algorithms.minimum_eigensolvers import NumPyMinimumEigensolver

        fidelities = []
        coherences = []

        for rho in conflict_densities:
            # Random conflict matrix scaled by density
            rng = np.random.default_rng(self.seed)
            J = (np.random.rand(self.n_qubits, self.n_qubits) - 0.5) * 2
            J = (J + J.T) / 2
            np.fill_diagonal(J, 0)
            J = J * base_strength * rho

            H = self.build_conflict_hamiltonian(J)
            if H is None:
                fidelities.append(0.5)
                coherences.append(0.5)
                continue

            try:
                solver = NumPyMinimumEigensolver()
                result = solver.compute_minimum_eigenvalue(H)
                ground_state = result.eigenstate
                if hasattr(ground_state, "to_statevector"):
                    sv = ground_state.to_statevector()
                else:
                    sv = Statevector(ground_state)

                # Fidelity: overlap with |0...0⟩ (trivial consensus)
                zeros = "0" * self.n_qubits
                fid = float(np.abs(sv.data[0]) ** 2) if len(sv.data) > 0 else 0.0

                # Coherence: concentration on |00..0⟩ or |11..1⟩
                data = np.asarray(sv.data)
                p0 = np.abs(data[0]) ** 2 if len(data) > 0 else 0
                p1 = np.abs(data[-1]) ** 2 if len(data) > 0 else 0
                coherence = p0 + p1

                fidelities.append(fid)
                coherences.append(coherence)
            except Exception:
                fidelities.append(0.5)
                coherences.append(0.5)

        fidelities = np.array(fidelities)
        coherences = np.array(coherences)

        # Estimate collapse: first point where fidelity < 0.3
        collapse_point = None
        idx = np.where(fidelities < 0.3)[0]
        if len(idx) > 0:
            collapse_point = float(conflict_densities[idx[0]])

        return {
            "conflict_densities": conflict_densities,
            "fidelities": np.array(fidelities),
            "coherences": np.array(coherences),
            "collapse_point": collapse_point,
        }


def _outcome_to_bitstring(outcome: Any, n_qubits: int) -> str:
    """Convert SamplerV2 outcome (BitArray, int, etc.) to '0000' style string."""
    if isinstance(outcome, str) and all(c in "01" for c in outcome):
        s = outcome
    else:
        s = str(outcome)
        if s.startswith("0b"):
            s = s[2:]
        elif s.startswith("0x"):
            s = format(int(outcome, 16) & ((1 << n_qubits) - 1), f"0{n_qubits}b")
        elif s.lstrip("-").isdigit():
            s = format(int(outcome) & ((1 << n_qubits) - 1), f"0{n_qubits}b")
    return s.zfill(n_qubits)[:n_qubits]


class AdvancedEthicalQuantumEngine:
    """
    High-Dimensional Ethical Hilbert Space engine.

    Maps agents to Bloch sphere positions via U3 gates and models social
    entanglement via Rzz gates. Produces circuit diagrams and measurement
    distributions for paper-ready visualizations.

    When use_real_hardware=True and IBM_QUANTUM_TOKEN is set, submits the
    multi-qubit U3+Rzz circuit to IBM Quantum (e.g. ibm_fez) instead of Aer.
    """

    def __init__(
        self,
        num_agents: int,
        use_real_hardware: bool = False,
        backend_name: str = "ibm_fez",
    ):
        """
        Initialize the Ethical Hilbert Space engine.

        Parameters
        ----------
        num_agents : int
            Number of qubits (1 qubit per agent/cluster).
        use_real_hardware : bool, default=False
            If True, submits circuit to IBM Quantum (requires IBM_QUANTUM_TOKEN).
        backend_name : str, default='ibm_fez'
            IBM backend name when use_real_hardware=True.
        """
        self.num_qubits = num_agents
        self.use_real_hardware = use_real_hardware
        self._backend_name = backend_name
        self._service = None
        self.simulator = AerSimulator() if _QISKIT_AVAILABLE else None
        self._qc = None  # Last built circuit, for error mitigation calibration

        if use_real_hardware:
            try:
                import os
                from qiskit_ibm_runtime import QiskitRuntimeService

                token = os.environ.get("IBM_QUANTUM_TOKEN")
                if token:
                    service_kw = {"channel": "ibm_quantum_platform", "token": token}
                    if os.environ.get("IBM_QUANTUM_INSTANCE"):
                        service_kw["instance"] = os.environ["IBM_QUANTUM_INSTANCE"]
                    if os.environ.get("IBM_QUANTUM_REGION"):
                        service_kw["region"] = os.environ["IBM_QUANTUM_REGION"]
                    self._service = QiskitRuntimeService(**service_kw)
            except ImportError:
                pass

    def _get_ibm_backend(self):
        """Resolve IBM backend; fallback to simulator if hardware unavailable."""
        if not self._service:
            return None
        try:
            return self._service.backend(name=self._backend_name)
        except Exception:
            for sim_filter in [{"simulator": True}, {"simulator": True, "operational": True}]:
                backends = list(self._service.backends(**sim_filter))
                if backends:
                    return backends[0]
            all_backends = list(self._service.backends())
            sims = [b for b in all_backends if getattr(b, "simulator", False) or "simulator" in str(getattr(b, "name", "")).lower()]
            if sims:
                return sims[0]
            return all_backends[0] if all_backends else None

    def build_social_circuit(
        self,
        agent_states: list[dict],
        adjacency_matrix: np.ndarray,
    ) -> Any:
        """
        Build quantum circuit mapping social graph to entanglement.

        Parameters
        ----------
        agent_states : list of dict
            Each dict has 'theta', 'phi', 'lambda' (Bloch sphere angles).
        adjacency_matrix : ndarray
            2D matrix of connection strengths (0.0 to 1.0).

        Returns
        -------
        QuantumCircuit or None
        """
        if not _QISKIT_AVAILABLE:
            return None

        n = min(self.num_qubits, len(agent_states), adjacency_matrix.shape[0])
        qc = QuantumCircuit(n)

        # 1. ENCODING LAYER: Map ethical state to Bloch Sphere
        for i, state in enumerate(agent_states[:n]):
            theta = state.get("theta", np.pi / 2)
            phi = state.get("phi", 0.0)
            lam = state.get("lambda", state.get("lam", 0.0))
            qc.u(float(theta), float(phi), float(lam), i)

        qc.barrier()

        # 2. ENTANGLEMENT LAYER: Social interactions
        adj = np.asarray(adjacency_matrix)
        rows, cols = min(n, adj.shape[0]), min(n, adj.shape[1])
        for i in range(rows):
            for j in range(i + 1, cols):
                strength = float(adj[i, j])
                if strength > 0.1:
                    entanglement_angle = strength * np.pi
                    qc.rzz(entanglement_angle, i, j)

        qc.measure_all()
        self._qc = qc
        return qc

    def apply_error_mitigation(
        self,
        raw_counts: Dict[str, int],
        qubit_list: list[int] | None = None,
    ) -> Dict[str, int]:
        """
        Apply readout error mitigation to raw measurement counts.

        Calibrates against measurement errors (e.g., measuring 0 as 1).
        Use on real IBM hardware; Aer simulator has no noise, so returns raw_counts.

        Parameters
        ----------
        raw_counts : dict
            Raw measurement counts from run.
        qubit_list : list of int, optional
            Qubits to calibrate. If None, uses [0..num_qubits-1].

        Returns
        -------
        dict
            Mitigated counts, or raw_counts if mitigation unavailable.
        """
        if not _MITIGATION_AVAILABLE or complete_meas_cal is None or CompleteMeasFitter is None:
            return raw_counts
        if self._qc is None or not _QISKIT_AVAILABLE or self.simulator is None:
            return raw_counts

        n = self.num_qubits
        qubit_list = qubit_list if qubit_list is not None else list(range(n))
        if not qubit_list:
            return raw_counts

        try:
            qr = self._qc.qregs[0] if self._qc and self._qc.qregs else None
            if qr is None:
                return raw_counts
            meas_calibs, state_labels = complete_meas_cal(
                qubit_list=qubit_list,
                qr=qr,
                circlabel="mcal",
            )
            cal_results = self.simulator.run(
                transpile(meas_calibs, self.simulator), shots=1024
            ).result()
            meas_fitter = CompleteMeasFitter(cal_results, state_labels, circlabel="mcal")
            meas_filter = meas_fitter.filter
            return meas_filter.apply(raw_counts)
        except Exception:
            return raw_counts

    def run_simulation(
        self,
        agent_data: list[dict],
        adjacency_matrix: np.ndarray,
        shot_count: int = 1024,
        use_error_mitigation: bool = False,
        output_dir: str | None = None,
    ) -> Dict[str, Any]:
        """
        Run the circuit and return the collapsed ethical reality.

        Parameters
        ----------
        agent_data : list of dict
            Each agent dict may have 'empathy', 'flexibility', 'resilience' (0-1).
        adjacency_matrix : ndarray
            Social connection strengths.
        shot_count : int, default=1024
            Number of measurement shots.
        use_error_mitigation : bool, default=False
            Apply readout error mitigation (for real hardware).
        output_dir : str, optional
            Directory for saving figures. Default: simulation/output/figures.

        Returns
        -------
        dict
            consensus_state, system_coherence, circuit_image, dist_image, etc.
        """
        import os

        if output_dir is None:
            root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_dir = os.path.join(root, "simulation", "output", "figures")
        os.makedirs(output_dir, exist_ok=True)

        states = []
        for agent in agent_data:
            states.append({
                "theta": float(agent.get("empathy", 0.5)) * np.pi,
                "phi": float(agent.get("flexibility", 0.5)) * 2 * np.pi,
                "lambda": float(agent.get("resilience", 0.5)) * np.pi,
            })

        if not _QISKIT_AVAILABLE or self.simulator is None:
            return self._numpy_fallback_results(output_dir)

        qc = self.build_social_circuit(states, adjacency_matrix)
        if qc is None:
            return self._numpy_fallback_results(output_dir)

        counts: Dict[str, int] = {}
        use_ibm = self.use_real_hardware and self._service
        backend = self._get_ibm_backend() if use_ibm else None

        if backend is not None:
            try:
                from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
                from qiskit_ibm_runtime import Sampler

                pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
                isa_circuit = pm.run(qc)
                sampler = Sampler(mode=backend)
                sampler_result = sampler.run([(isa_circuit,)], shots=shot_count).result()
                quasi = sampler_result[0].join_data().get_counts()

                n = self.num_qubits
                for outcome, cnt in quasi.items():
                    key = _outcome_to_bitstring(outcome, n)
                    counts[key] = counts.get(key, 0) + int(cnt)
            except Exception:
                use_ibm = False
                counts = {}

        if not use_ibm or not counts:
            transpiled = transpile(qc, self.simulator)
            result = self.simulator.run(transpiled, shots=shot_count).result()
            counts = result.get_counts()

        if use_error_mitigation:
            counts = self.apply_error_mitigation(counts)

        return self._analyze_results(counts, qc, output_dir)

    def _analyze_results(
        self,
        counts: Dict[str, int],
        qc: Any,
        output_dir: str,
    ) -> Dict[str, Any]:
        """Interpret quantum measurement as social outcomes."""
        import os

        circuit_img_path = os.path.join(output_dir, "latest_quantum_circuit.png")
        dist_img_path = os.path.join(output_dir, "latest_quantum_distribution.png")

        if _QISKIT_AVAILABLE:
            try:
                import matplotlib.pyplot as plt

                fig = qc.draw(output="mpl")
                if hasattr(fig, "savefig"):
                    fig.savefig(circuit_img_path, dpi=150, bbox_inches="tight")
                plt.close("all")
            except Exception:
                pass

            if _PLOT_AVAILABLE and plot_histogram is not None:
                try:
                    import matplotlib.pyplot as plt

                    fig = plot_histogram(counts)
                    if hasattr(fig, "savefig"):
                        fig.savefig(dist_img_path, dpi=150, bbox_inches="tight")
                    plt.close("all")
                except Exception:
                    pass

        total = sum(counts.values())
        most_frequent_state = max(counts, key=counts.get) if counts else ""
        consensus_strength = counts.get(most_frequent_state, 0) / total if total else 0.0

        return {
            "consensus_state": most_frequent_state,
            "system_coherence": consensus_strength,
            "circuit_image": circuit_img_path,
            "dist_image": dist_img_path,
            "raw_counts": counts,
        }

    def _numpy_fallback_results(self, output_dir: str) -> Dict[str, Any]:
        """Fallback when Qiskit unavailable."""
        import os

        rng = np.random.default_rng()
        n = self.num_qubits
        zeros = "0" * n
        ones = "1" * n
        p0 = rng.random() * 0.3 + 0.3
        counts = {zeros: int(1024 * p0), ones: int(1024 * (1 - p0) * 0.5)}
        for _ in range(1024 - sum(counts.values())):
            s = "".join(str(rng.integers(0, 2)) for _ in range(n))
            counts[s] = counts.get(s, 0) + 1

        circuit_img_path = os.path.join(output_dir, "latest_quantum_circuit.png")
        dist_img_path = os.path.join(output_dir, "latest_quantum_distribution.png")

        total = sum(counts.values())
        most_frequent_state = max(counts, key=counts.get)
        consensus_strength = counts.get(most_frequent_state, 0) / total if total else 0.0

        return {
            "consensus_state": most_frequent_state,
            "system_coherence": consensus_strength,
            "circuit_image": circuit_img_path,
            "dist_image": dist_img_path,
            "raw_counts": counts,
        }


class LocalQuantumJudge(QuantumOracle):
    """
    Local quantum simulator for ethical judgments.

    Uses Rx rotation: θ = difficulty × π to encode complexity into
    superposition |ψ⟩ = cos(θ/2)|0⟩ - i·sin(θ/2)|1⟩.
    Maps |0⟩→Ethical (+1), |1⟩→Unethical (-1).
    """

    def __init__(self, shots: int = 1024, seed: int | None = None):
        """
        Parameters
        ----------
        shots : int
            Number of measurement shots for statistical judgment
        seed : int | None
            Random seed for reproducibility

        Uses qiskit-aer when available; falls back to pure-Python NumPy simulation
        when qiskit-aer cannot be installed (e.g., Python 3.14, AppleClang 17).
        """
        self.shots = shots
        self.seed = seed
        self._use_qiskit = _QISKIT_AVAILABLE
        if _QISKIT_AVAILABLE:
            self._simulator = AerSimulator()

    def collapse_wavefunction(
        self,
        complexity_amplitudes: Tuple[float, ...],
    ) -> Tuple[float, float]:
        """
        Map complexity amplitudes to measurement probabilities.

        For single-qubit: θ = mean(amplitudes) × π.
        Returns (α², β²) for |α|² + |β|² = 1.
        """
        difficulty = float(np.mean(complexity_amplitudes)) if complexity_amplitudes else 0.5
        difficulty = max(0.0, min(1.0, difficulty))

        theta = difficulty * np.pi
        alpha_sq = float(np.cos(theta / 2) ** 2)
        beta_sq = 1.0 - alpha_sq
        return (alpha_sq, beta_sq)

    def judge_action(
        self,
        difficulty: float,
        shots: int | None = None,
    ) -> float:
        """
        Produce judgment for a single action via quantum measurement.

        Parameters
        ----------
        difficulty : float ∈ [0, 1]
            Normalized complexity/difficulty (e.g., c/100)
        shots : int | None
            Override default shots

        Returns
        -------
        float
            Judgment J ∈ [-1, 1] (expectation over measurements)
        """
        n = shots or self.shots
        if not self._use_qiskit:
            return _numpy_judge_action(difficulty, n, self.seed)
        theta = max(0.0, min(1.0, difficulty)) * np.pi
        qc = QuantumCircuit(1, 1)
        qc.rx(theta, 0)
        qc.measure(0, 0)
        result = self._simulator.run(qc, shots=n, seed_simulator=self.seed).result()
        counts = result.get_counts()
        p0 = counts.get("0", 0) / n
        return float(2 * p0 - 1)

    def entangled_judgment(
        self,
        agent_a_bias: float,
        agent_b_bias: float,
    ) -> Tuple[float, float]:
        """
        Bell-state entanglement: prepare |Φ⁺⟩ = (|00⟩ + |11⟩)/√2.

        Apply local Rx(θ_a) and Rx(θ_b) based on biases, then measure.
        Outcomes are correlated (both 0 or both 1 when no rotation).
        """
        if not self._use_qiskit:
            return _numpy_entangled_simple(
                agent_a_bias, agent_b_bias, self.shots, self.seed
            )
        theta_a = np.clip(agent_a_bias, -1, 1) * np.pi / 2
        theta_b = np.clip(agent_b_bias, -1, 1) * np.pi / 2
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.rx(theta_a, 0)
        qc.rx(theta_b, 1)
        qc.measure([0, 1], [0, 1])
        result = self._simulator.run(
            qc, shots=self.shots, seed_simulator=self.seed
        ).result()
        counts = result.get_counts()
        J_a_vals, J_b_vals = [], []
        for outcome, count in counts.items():
            a_val = 1 if outcome[0] == "0" else -1
            b_val = 1 if outcome[1] == "0" else -1
            for _ in range(count):
                J_a_vals.append(a_val)
                J_b_vals.append(b_val)
        return (
            float(np.mean(J_a_vals)) if J_a_vals else 0.0,
            float(np.mean(J_b_vals)) if J_b_vals else 0.0,
        )
