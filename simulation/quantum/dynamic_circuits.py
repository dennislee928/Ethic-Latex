"""
Dynamic Circuit Generation from time-series (§2.2).

Given a time-series of social interactions (e.g., rolling sentiment scores
or pairwise interaction weights), automatically construct a parameterised
quantum circuit whose RZZ / RX angles track the data.  Works purely on
NumPy when qiskit is unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    _QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover
    _QISKIT_AVAILABLE = False
    QuantumCircuit = None  # type: ignore
    Statevector = None  # type: ignore


__all__ = [
    "TimeStep",
    "build_dynamic_circuit",
    "compile_time_series",
    "run_dynamic_evolution",
    "pairwise_from_correlation_matrix",
]


@dataclass
class TimeStep:
    """
    One time-slice of societal data.

    couplings  :  list of (i, j, J_ij) pairwise interaction weights
    fields     :  length-n list of local transverse-field h_i values
    dt         :  effective Trotter step (time spent in this slice)
    """
    couplings: List[Tuple[int, int, float]] = field(default_factory=list)
    fields: List[float] = field(default_factory=list)
    dt: float = 1.0


def pairwise_from_correlation_matrix(
    corr: np.ndarray,
    threshold: float = 1e-6,
) -> List[Tuple[int, int, float]]:
    """Turn a correlation matrix into sparse (i, j, J_ij) triples (upper tri)."""
    n = corr.shape[0]
    out: List[Tuple[int, int, float]] = []
    for i in range(n):
        for j in range(i + 1, n):
            v = float(corr[i, j])
            if abs(v) >= threshold:
                out.append((i, j, v))
    return out


def compile_time_series(
    interaction_series: Sequence[np.ndarray],
    field_series: Sequence[Sequence[float]],
    dt: float = 1.0,
    coupling_threshold: float = 1e-6,
) -> List[TimeStep]:
    """
    Convert a time-series of (interaction matrix, field vector) into a list of
    TimeStep objects suitable for `build_dynamic_circuit`.
    """
    if len(interaction_series) != len(field_series):
        raise ValueError("interaction_series and field_series must align")
    steps: List[TimeStep] = []
    for J, h in zip(interaction_series, field_series):
        steps.append(TimeStep(
            couplings=pairwise_from_correlation_matrix(np.asarray(J), coupling_threshold),
            fields=list(h),
            dt=float(dt),
        ))
    return steps


def build_dynamic_circuit(
    n_qubits: int,
    time_series: Sequence[TimeStep],
    initial_state: str = "plus",
) -> Any:
    """
    Build a dynamic Trotter circuit from a time-series.  Returns a qiskit
    QuantumCircuit if available, otherwise a NumPy-executable description
    (list of ("rzz"/"rx", qubits, angle) tuples).

    initial_state: "plus" applies Hadamard on all qubits (uniform superposition),
                   "zero" leaves |00...0>, "random" applies random single-qubit rotations.
    """
    if _QISKIT_AVAILABLE:
        qc = QuantumCircuit(n_qubits)
        if initial_state == "plus":
            for q in range(n_qubits):
                qc.h(q)
        elif initial_state == "random":
            rng = np.random.default_rng(0)
            for q in range(n_qubits):
                qc.ry(float(rng.uniform(0, np.pi)), q)
        for step in time_series:
            for (i, j, J) in step.couplings:
                qc.rzz(2.0 * J * step.dt, i, j)
            for q, h in enumerate(step.fields):
                if h != 0.0:
                    qc.rx(2.0 * h * step.dt, q)
        return qc

    # NumPy fallback: return symbolic tape
    tape: List[Tuple[str, Tuple[int, ...], float]] = []
    if initial_state == "plus":
        for q in range(n_qubits):
            tape.append(("h", (q,), 0.0))
    for step in time_series:
        for (i, j, J) in step.couplings:
            tape.append(("rzz", (i, j), 2.0 * J * step.dt))
        for q, h in enumerate(step.fields):
            if h != 0.0:
                tape.append(("rx", (q,), 2.0 * h * step.dt))
    return tape


# ---------------------------------------------------------------------------
# Pure-NumPy executor for the fallback tape
# ---------------------------------------------------------------------------

def _apply_gate(state: np.ndarray, name: str, qubits: Tuple[int, ...],
                theta: float, n: int) -> np.ndarray:
    I = np.eye(2, dtype=complex)
    if name == "h":
        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2.0)
        return _apply_1q(state, H, qubits[0], n)
    if name == "rx":
        c, s = np.cos(theta / 2.0), np.sin(theta / 2.0)
        g = np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)
        return _apply_1q(state, g, qubits[0], n)
    if name == "rzz":
        # exp(-i*theta/2 Z Z); diagonal in computational basis
        i, j = qubits
        out = state.copy()
        for idx in range(1 << n):
            zi = 1 if (idx >> i) & 1 == 0 else -1
            zj = 1 if (idx >> j) & 1 == 0 else -1
            phase = np.exp(-1j * theta / 2.0 * zi * zj)
            out[idx] = out[idx] * phase
        return out
    raise ValueError(f"unknown gate {name}")


def _apply_1q(state: np.ndarray, gate: np.ndarray, q: int, n: int) -> np.ndarray:
    out = np.zeros_like(state)
    bit = 1 << q
    for idx in range(1 << n):
        if idx & bit:
            continue
        i0 = idx
        i1 = idx | bit
        a0, a1 = state[i0], state[i1]
        out[i0] = gate[0, 0] * a0 + gate[0, 1] * a1
        out[i1] = gate[1, 0] * a0 + gate[1, 1] * a1
    return out


def run_dynamic_evolution(
    n_qubits: int,
    time_series: Sequence[TimeStep],
    initial_state: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Evolve an initial state under the time-series Trotter circuit using the
    pure-NumPy fallback executor.  Returns the resulting state vector.
    """
    if initial_state is None:
        state = np.zeros(1 << n_qubits, dtype=complex)
        state[0] = 1.0
        # apply H on all qubits
        for q in range(n_qubits):
            state = _apply_gate(state, "h", (q,), 0.0, n_qubits)
    else:
        state = initial_state.astype(complex).copy()

    tape = build_dynamic_circuit(n_qubits, time_series, initial_state="zero")
    # `tape` will be a qiskit QuantumCircuit OR a NumPy list
    if _QISKIT_AVAILABLE and hasattr(tape, "data"):
        # Convert qiskit tape into the simple tape by re-generating.
        tape = _qiskit_tape_equivalent(n_qubits, time_series)

    for name, qubits, theta in tape:
        state = _apply_gate(state, name, qubits, theta, n_qubits)
    # Renormalise
    nrm = np.linalg.norm(state)
    if nrm > 0:
        state /= nrm
    return state


def _qiskit_tape_equivalent(n_qubits: int, time_series: Sequence[TimeStep]
                            ) -> List[Tuple[str, Tuple[int, ...], float]]:
    tape: List[Tuple[str, Tuple[int, ...], float]] = []
    for step in time_series:
        for (i, j, J) in step.couplings:
            tape.append(("rzz", (i, j), 2.0 * J * step.dt))
        for q, h in enumerate(step.fields):
            if h != 0.0:
                tape.append(("rx", (q,), 2.0 * h * step.dt))
    return tape
