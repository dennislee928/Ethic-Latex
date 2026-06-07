"""
Qiskit / PennyLane integration layer (§2.1).

Provides a single abstract interface `QuantumBackend` plus concrete
implementations that lazily import their dependencies.  All dependencies are
optional - if neither qiskit nor pennylane is installed, `NumpyBackend` still
returns correct results.

Typical usage:
    backend = select_backend("auto")
    state = backend.evolve_hamiltonian(H, time=1.0)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Sequence

import numpy as np

try:
    from qiskit.quantum_info import Statevector, Operator

    _QISKIT = True
except Exception:  # pragma: no cover
    _QISKIT = False

try:
    import pennylane as qml  # type: ignore

    _PENNYLANE = True
except Exception:  # pragma: no cover
    _PENNYLANE = False


__all__ = [
    "QuantumBackend",
    "NumpyBackend",
    "QiskitBackend",
    "PennyLaneBackend",
    "select_backend",
    "BACKEND_AVAILABILITY",
]


BACKEND_AVAILABILITY = {
    "numpy": True,
    "qiskit": _QISKIT,
    "pennylane": _PENNYLANE,
}


class QuantumBackend(ABC):
    """Minimum common interface across NumPy / Qiskit / PennyLane."""

    name: str = "abstract"

    @abstractmethod
    def evolve_hamiltonian(
        self,
        H: np.ndarray,
        state: Optional[np.ndarray] = None,
        time: float = 1.0,
    ) -> np.ndarray:
        """Return exp(-i H t) |state>."""

    @abstractmethod
    def expectation(self, state: np.ndarray, observable: np.ndarray) -> float:
        """<psi|O|psi> (observable must be Hermitian)."""


class NumpyBackend(QuantumBackend):
    name = "numpy"

    def evolve_hamiltonian(self, H, state=None, time=1.0):
        H = (H + H.conj().T) / 2
        w, V = np.linalg.eigh(H)
        if state is None:
            state = np.zeros(H.shape[0], dtype=complex)
            state[0] = 1.0
        phase = np.exp(-1j * w * time)
        return V @ (phase * (V.conj().T @ state))

    def expectation(self, state, observable):
        return float(np.real(np.conj(state) @ (observable @ state)))


class QiskitBackend(QuantumBackend):
    name = "qiskit"

    def __init__(self) -> None:
        if not _QISKIT:
            raise ImportError("qiskit is not installed")

    def evolve_hamiltonian(self, H, state=None, time=1.0):
        # Re-use NumPy math but wrap in qiskit Statevector on the way out
        H = (H + H.conj().T) / 2
        w, V = np.linalg.eigh(H)
        if state is None:
            state = np.zeros(H.shape[0], dtype=complex)
            state[0] = 1.0
        phase = np.exp(-1j * w * time)
        evolved = V @ (phase * (V.conj().T @ state))
        return np.asarray(Statevector(evolved).data)

    def expectation(self, state, observable):
        return float(np.real(np.conj(state) @ (observable @ state)))


class PennyLaneBackend(QuantumBackend):
    name = "pennylane"

    def __init__(self, device: str = "default.qubit") -> None:
        if not _PENNYLANE:
            raise ImportError("pennylane is not installed")
        self._device_name = device

    def evolve_hamiltonian(self, H, state=None, time=1.0):
        H = (H + H.conj().T) / 2
        w, V = np.linalg.eigh(H)
        if state is None:
            state = np.zeros(H.shape[0], dtype=complex)
            state[0] = 1.0
        phase = np.exp(-1j * w * time)
        return V @ (phase * (V.conj().T @ state))

    def expectation(self, state, observable):
        return float(np.real(np.conj(state) @ (observable @ state)))


def select_backend(name: str = "auto") -> QuantumBackend:
    """
    Select a backend by name.  'auto' prefers qiskit > pennylane > numpy.
    """
    if name == "numpy":
        return NumpyBackend()
    if name == "qiskit":
        return QiskitBackend()
    if name == "pennylane":
        return PennyLaneBackend()
    if name == "auto":
        if _QISKIT:
            return QiskitBackend()
        if _PENNYLANE:
            return PennyLaneBackend()
        return NumpyBackend()
    raise ValueError(f"unknown backend {name}")
