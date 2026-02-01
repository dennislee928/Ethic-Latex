"""
Local Quantum Judge using Qiskit AerSimulator.

Maps difficulty to θ = difficulty × π for Rx rotation.
Measurement of superposition yields judgment in [-1, 1].
"""

from typing import Tuple

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from qiskit.quantum_info import Statevector
    import numpy as np

    _QISKIT_AVAILABLE = True
except ImportError:
    _QISKIT_AVAILABLE = False
    np = None

from .interface import QuantumOracle


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
        """
        if not _QISKIT_AVAILABLE:
            raise ImportError(
                "qiskit and qiskit-aer required for LocalQuantumJudge. "
                "Install with: pip install qiskit qiskit-aer"
            )
        self.shots = shots
        self.seed = seed
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
        shots = shots or self.shots
        theta = max(0.0, min(1.0, difficulty)) * np.pi

        qc = QuantumCircuit(1, 1)
        qc.rx(theta, 0)
        qc.measure(0, 0)

        result = self._simulator.run(
            qc,
            shots=shots,
            seed_simulator=self.seed,
        ).result()

        counts = result.get_counts()
        p0 = counts.get("0", 0) / shots
        p1 = counts.get("1", 0) / shots
        return float(2 * p0 - 1)  # map 0→+1, 1→-1

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
        theta_a = np.clip(agent_a_bias, -1, 1) * np.pi / 2
        theta_b = np.clip(agent_b_bias, -1, 1) * np.pi / 2

        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.rx(theta_a, 0)
        qc.rx(theta_b, 1)
        qc.measure([0, 1], [0, 1])

        result = self._simulator.run(
            qc,
            shots=self.shots,
            seed_simulator=self.seed,
        ).result()

        counts = result.get_counts()
        J_a_vals = []
        J_b_vals = []
        for outcome, count in counts.items():
            a_val = 1 if outcome[0] == "0" else -1
            b_val = 1 if outcome[1] == "0" else -1
            for _ in range(count):
                J_a_vals.append(a_val)
                J_b_vals.append(b_val)

        J_a = float(np.mean(J_a_vals)) if J_a_vals else 0.0
        J_b = float(np.mean(J_b_vals)) if J_b_vals else 0.0
        return (J_a, J_b)
