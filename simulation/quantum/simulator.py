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
