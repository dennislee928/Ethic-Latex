"""
Heisenberg (XXZ / XYZ) Moral Hamiltonian (§3.1).

Extends the Transverse-Field Ising model to continuous moral variables
with anisotropic interactions:

    H = sum_{<i,j>} [ Jx X_i X_j + Jy Y_i Y_j + Jz Z_i Z_j ] + sum_i h_i Z_i

Returns both a dense NumPy Hermitian operator and, when Qiskit is available,
an equivalent SparsePauliOp.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple, Any

import numpy as np

try:
    from qiskit.quantum_info import SparsePauliOp

    _QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover
    _QISKIT_AVAILABLE = False
    SparsePauliOp = None  # type: ignore[assignment]

__all__ = [
    "pauli_matrices",
    "build_xxz_hamiltonian",
    "build_xyz_hamiltonian",
    "build_heisenberg_sparse_paulis",
    "heisenberg_ground_state",
]

# ---------------------------------------------------------------------------
# Pauli helpers (kept here so the module is self-contained)
# ---------------------------------------------------------------------------

_I = np.array([[1, 0], [0, 1]], dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def pauli_matrices() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return _I.copy(), _X.copy(), _Y.copy(), _Z.copy()


def _embed_two_qubit(op_a: np.ndarray, op_b: np.ndarray,
                     qubits: Tuple[int, int], n: int) -> np.ndarray:
    """Embed op_a on qubit qubits[0], op_b on qubit qubits[1] into n-qubit space.

    Little-endian convention: qubit 0 is the LEAST significant bit, which means
    the first factor in the Kronecker product is qubit n-1.  We build the big
    operator by iterating from qubit n-1 down to 0.
    """
    mats = [_I] * n
    mats[qubits[0]] = op_a
    mats[qubits[1]] = op_b
    return _kron_list(mats)


def _embed_one_qubit(op: np.ndarray, q: int, n: int) -> np.ndarray:
    mats = [_I] * n
    mats[q] = op
    return _kron_list(mats)


def _kron_list(mats: Sequence[np.ndarray]) -> np.ndarray:
    """Kronecker product ordered qubit n-1, n-2, ..., 0 (little-endian)."""
    out = np.array([[1.0]], dtype=complex)
    for m in reversed(mats):  # reverse so qubit 0 is innermost
        out = np.kron(out, m)
    return out


# ---------------------------------------------------------------------------
# Hamiltonian builders
# ---------------------------------------------------------------------------

def _edges_from_topology(n: int, topology: str) -> List[Tuple[int, int]]:
    if topology == "linear":
        return [(i, i + 1) for i in range(n - 1)]
    if topology == "ring":
        return [(i, (i + 1) % n) for i in range(n)]
    if topology == "full":
        return [(i, j) for i in range(n) for j in range(i + 1, n)]
    raise ValueError(f"unknown topology {topology}")


def build_xxz_hamiltonian(
    n: int,
    Jxy: float = 1.0,
    Jz: float = 1.0,
    fields: Optional[Sequence[float]] = None,
    edges: Optional[Iterable[Tuple[int, int]]] = None,
    topology: str = "linear",
) -> np.ndarray:
    """
    XXZ Hamiltonian:  H = Jxy * sum (X_i X_j + Y_i Y_j) + Jz * sum Z_i Z_j
                       + sum_i h_i Z_i
    """
    if fields is None:
        fields = [0.0] * n
    if len(fields) != n:
        raise ValueError("fields length mismatch")
    if edges is None:
        edges = _edges_from_topology(n, topology)

    dim = 1 << n
    H = np.zeros((dim, dim), dtype=complex)

    for i, j in edges:
        H += Jxy * (_embed_two_qubit(_X, _X, (i, j), n)
                    + _embed_two_qubit(_Y, _Y, (i, j), n))
        H += Jz * _embed_two_qubit(_Z, _Z, (i, j), n)

    for i, h in enumerate(fields):
        if h != 0.0:
            H += h * _embed_one_qubit(_Z, i, n)

    return H


def build_xyz_hamiltonian(
    n: int,
    Jx: float = 1.0,
    Jy: float = 1.0,
    Jz: float = 1.0,
    fields: Optional[Sequence[float]] = None,
    edges: Optional[Iterable[Tuple[int, int]]] = None,
    topology: str = "linear",
) -> np.ndarray:
    """XYZ generalisation with independent Jx, Jy, Jz."""
    if fields is None:
        fields = [0.0] * n
    if len(fields) != n:
        raise ValueError("fields length mismatch")
    if edges is None:
        edges = _edges_from_topology(n, topology)

    dim = 1 << n
    H = np.zeros((dim, dim), dtype=complex)

    for i, j in edges:
        H += Jx * _embed_two_qubit(_X, _X, (i, j), n)
        H += Jy * _embed_two_qubit(_Y, _Y, (i, j), n)
        H += Jz * _embed_two_qubit(_Z, _Z, (i, j), n)

    for i, h in enumerate(fields):
        if h != 0.0:
            H += h * _embed_one_qubit(_Z, i, n)
    return H


def build_heisenberg_sparse_paulis(
    n: int,
    Jx: float = 1.0,
    Jy: float = 1.0,
    Jz: float = 1.0,
    fields: Optional[Sequence[float]] = None,
    edges: Optional[Iterable[Tuple[int, int]]] = None,
    topology: str = "linear",
) -> Any:
    """Return a Qiskit SparsePauliOp when qiskit is installed; else None."""
    if not _QISKIT_AVAILABLE:
        return None
    fields = fields or [0.0] * n
    if edges is None:
        edges = _edges_from_topology(n, topology)

    terms: List[Tuple[str, float]] = []

    def pauli_str(ops: dict) -> str:
        s = ["I"] * n
        for q, p in ops.items():
            # Qiskit uses little-endian: qubit 0 is rightmost char
            s[n - 1 - q] = p
        return "".join(s)

    for i, j in edges:
        if Jx != 0.0:
            terms.append((pauli_str({i: "X", j: "X"}), Jx))
        if Jy != 0.0:
            terms.append((pauli_str({i: "Y", j: "Y"}), Jy))
        if Jz != 0.0:
            terms.append((pauli_str({i: "Z", j: "Z"}), Jz))

    for i, h in enumerate(fields):
        if h != 0.0:
            terms.append((pauli_str({i: "Z"}), float(h)))

    if not terms:
        terms.append(("I" * n, 0.0))
    return SparsePauliOp.from_list(terms)


def heisenberg_ground_state(
    n: int,
    Jx: float = 1.0,
    Jy: float = 1.0,
    Jz: float = 1.0,
    fields: Optional[Sequence[float]] = None,
    topology: str = "linear",
) -> Tuple[float, np.ndarray]:
    """Return (ground_energy, ground_state_vector) by exact diagonalisation."""
    H = build_xyz_hamiltonian(n, Jx, Jy, Jz, fields, topology=topology)
    H = (H + H.conj().T) / 2  # enforce Hermitian cleanup
    eigvals, eigvecs = np.linalg.eigh(H)
    return float(eigvals[0]), eigvecs[:, 0]
