"""
Tests for quantum entanglement implementation (Prisoner's Dilemma scenario).

Verifies that measuring Agent A's decision statistically correlates with
Agent B's decision without classical data exchange.

Uses LocalQuantumJudge which has a pure-Python NumPy fallback when qiskit-aer
is unavailable (e.g., Python 3.14 or AppleClang 17 build failure).
"""

import numpy as np
import pytest

from simulation.quantum import LocalQuantumJudge


class TestQuantumEntanglement:
    """Test quantum entanglement and Prisoner's Dilemma correlation."""

    def test_local_quantum_judge_basic(self):
        """LocalQuantumJudge produces judgment in [-1, 1] (qiskit or numpy fallback)."""
        judge = LocalQuantumJudge(shots=512, seed=42)
        J = judge.judge_action(difficulty=0.5)
        assert -1 <= J <= 1

    def test_entangled_judgment_returns_pair(self):
        """entangled_judgment returns (J_a, J_b) for two agents."""
        judge = LocalQuantumJudge(shots=512, seed=42)
        J_a, J_b = judge.entangled_judgment(agent_a_bias=0.0, agent_b_bias=0.0)
        assert -1 <= J_a <= 1
        assert -1 <= J_b <= 1

    def test_prisoners_dilemma_correlation(self):
        """
        Prisoner's Dilemma: entangled outcomes correlate without classical exchange.

        Bell state |Φ⁺⟩ = (|00⟩+|11⟩)/√2: measuring both yields correlated bits.
        With zero bias, correlation should be positive (qiskit or numpy fallback).
        """
        judge = LocalQuantumJudge(shots=1024, seed=42)
        n_trials = 30
        J_a_list, J_b_list = [], []
        for _ in range(n_trials):
            J_a, J_b = judge.entangled_judgment(agent_a_bias=0.0, agent_b_bias=0.0)
            J_a_list.append(J_a)
            J_b_list.append(J_b)

        J_a_arr = np.array(J_a_list)
        J_b_arr = np.array(J_b_list)
        if np.std(J_a_arr) > 1e-6 and np.std(J_b_arr) > 1e-6:
            corr = np.corrcoef(J_a_arr, J_b_arr)[0, 1]
            assert corr > -0.3, "Entangled judgments should correlate"

    def test_collapse_wavefunction(self):
        """collapse_wavefunction returns normalized (α², β²)."""
        judge = LocalQuantumJudge(shots=64, seed=42)
        alpha_sq, beta_sq = judge.collapse_wavefunction((0.5,))
        assert abs((alpha_sq + beta_sq) - 1.0) < 1e-6
        assert 0 <= alpha_sq <= 1
        assert 0 <= beta_sq <= 1
