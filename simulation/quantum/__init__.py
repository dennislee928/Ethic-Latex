"""
Quantum Judgment: non-binary ethical calculations using quantum mechanics.

Provides QuantumOracle interface and implementations (LocalQuantumJudge,
CloudQuantumJudge) for superposition-based ethical judgments.
"""

from .interface import QuantumOracle
from .simulator import LocalQuantumJudge

__all__ = ["QuantumOracle", "LocalQuantumJudge"]

try:
    from .cloud import CloudQuantumJudge

    __all__.append("CloudQuantumJudge")
except (ImportError, ValueError):
    CloudQuantumJudge = None  # qiskit-ibm-runtime or IBM_QUANTUM_TOKEN
