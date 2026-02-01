"""
Local Quantum Judge using Qiskit AerSimulator (or pure-Python fallback).

Maps difficulty to θ = difficulty × π for Rx rotation.
Measurement of superposition yields judgment in [-1, 1].

When qiskit-aer is unavailable (e.g., Python 3.14 or AppleClang 17 build failure),
a NumPy-based fallback is used so the quantum module still works.
"""

from typing import Tuple

import numpy as np

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    _QISKIT_AVAILABLE = True
except ImportError:
    _QISKIT_AVAILABLE = False

from .interface import QuantumOracle


def _numpy_judge_action(difficulty: float, shots: int, seed: int | None) -> float:
    """Pure-Python fallback: Rx(θ)|0⟩, P(0)=cos²(θ/2)."""
    rng = np.random.default_rng(seed)
    theta = max(0.0, min(1.0, difficulty)) * np.pi
    p0 = float(np.cos(theta / 2) ** 2)
    ones = int(rng.binomial(shots, p0))
    return float(2 * ones / shots - 1)


def _numpy_entangled_judgment(
    agent_a_bias: float,
    agent_b_bias: float,
    shots: int,
    seed: int | None,
) -> Tuple[float, float]:
    """Pure-Python fallback: Bell state + Rx, sample correlated outcomes."""
    rng = np.random.default_rng(seed)
    theta_a = np.clip(agent_a_bias, -1, 1) * np.pi / 2
    theta_b = np.clip(agent_b_bias, -1, 1) * np.pi / 2
    # 4x4 state: |Φ⁺⟩ = (|00⟩+|11⟩)/√2, then Rx_a ⊗ Rx_b
    phi_plus = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    # Rx(θ) = cos(θ/2)I - i·sin(θ/2)X for single qubit
    def rx_matrix(t):
        c, s = np.cos(t / 2), np.sin(t / 2)
        return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)
    Ra, Rb = rx_matrix(theta_a), rx_matrix(theta_b)
    U = np.kron(Ra, Rb)
    state = U @ phi_plus
    probs = np.abs(state) ** 2
    outcomes = rng.choice(4, size=shots, p=probs)
    J_a = float(2 * np.mean(outcomes in (0, 2) or outcomes < 2) - 1)
    # outcomes 0=|00⟩, 1=|01⟩, 2=|10⟩, 3=|11⟩; qubit0=outcome//2, qubit1=outcome%2
    q0 = (outcomes // 2).astype(float) * 2 - 1  # 0→-1, 1→+1
    q1 = (outcomes % 2).astype(float) * 2 - 1
    return (float(np.mean(q0)), float(np.mean(q1)))


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
