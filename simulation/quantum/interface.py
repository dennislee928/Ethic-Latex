"""
Quantum Oracle interface for non-binary ethical judgments.

Judgments are measurements of a superposition state:
  |ψ⟩ = α|Ethical⟩ + β|Unethical⟩
"""

from abc import ABC, abstractmethod
from typing import Tuple


class QuantumOracle(ABC):
    """
    Abstract base class for quantum-based ethical judgment oracles.

    Maps classical inputs (complexity, bias) to quantum operations and
    measurements representing ethical judgments.
    """

    @abstractmethod
    def collapse_wavefunction(
        self,
        complexity_amplitudes: Tuple[float, ...],
    ) -> Tuple[float, float]:
        """
        Collapse superposition state to measurement outcome.

        Parameters
        ----------
        complexity_amplitudes : tuple of float
            Amplitudes encoding difficulty/complexity per dimension

        Returns
        -------
        (alpha, beta) : tuple
            Amplitudes |α|² + |β|² = 1 for |ψ⟩ = α|E⟩ + β|U⟩
        """
        pass

    @abstractmethod
    def entangled_judgment(
        self,
        agent_a_bias: float,
        agent_b_bias: float,
    ) -> Tuple[float, float]:
        """
        Produce correlated judgments for two entangled agents (e.g., Prisoner's Dilemma).

        Agent A and B share entanglement; measuring one correlates with the other.

        Parameters
        ----------
        agent_a_bias : float
            Bias/preference of agent A ∈ [-1, 1]
        agent_b_bias : float
            Bias/preference of agent B ∈ [-1, 1]

        Returns
        -------
        (J_a, J_b) : tuple
            Judgment values for each agent
        """
        pass
