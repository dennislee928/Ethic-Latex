"""
Entanglement metrics (§2.3 of QUANTUM_SIMULATION_PLANS.md):

    * Concurrence        - two-qubit mixed-state entanglement (Wootters, 1998)
    * Negativity         - bipartite entanglement from partial transpose
    * Logarithmic negativity
    * Purity / linear entropy
    * Von Neumann entropy of a subsystem
    * A lower-bound proxy for quantum discord (Gaussian-style surrogate based
      on classical correlations) - clearly named as a proxy because full
      discord is NP-hard for arbitrary states.

All functions take NumPy arrays only - no Qiskit dependency.
"""

from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np

__all__ = [
    "partial_trace",
    "partial_transpose",
    "concurrence",
    "negativity",
    "logarithmic_negativity",
    "purity",
    "linear_entropy",
    "von_neumann_entropy",
    "discord_proxy",
    "mutual_information",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _state_to_density(state_or_rho: np.ndarray) -> np.ndarray:
    """Accept a pure state vector or density matrix; return density matrix."""
    arr = np.asarray(state_or_rho, dtype=complex)
    if arr.ndim == 1:
        return np.outer(arr, np.conj(arr))
    if arr.ndim == 2 and arr.shape[0] == arr.shape[1]:
        return arr
    raise ValueError("expected state vector or square density matrix")


def _dims_from_n(rho: np.ndarray) -> int:
    dim = rho.shape[0]
    n = int(round(np.log2(dim)))
    if (1 << n) != dim:
        raise ValueError("density matrix dimension is not a power of 2")
    return n


def partial_trace(
    rho: np.ndarray,
    keep: Sequence[int],
    dims: Sequence[int] | None = None,
) -> np.ndarray:
    """
    Partial trace of a multi-qubit density matrix, keeping the qubits listed
    in `keep`.

    Parameters
    ----------
    rho : ndarray
        State vector or density matrix.
    keep : sequence of int
        Qubit indices (0-based) to keep.
    dims : sequence of int | None
        Local dimensions; default is all 2's.
    """
    rho = _state_to_density(rho)
    n = _dims_from_n(rho) if dims is None else len(dims)
    dims = list(dims) if dims is not None else [2] * n
    if max(keep) >= n:
        raise ValueError("keep index out of range")

    # Reshape density matrix to a rank-2n tensor
    shape = dims + dims
    tensor = rho.reshape(shape)

    axes_to_trace = [i for i in range(n) if i not in keep]
    for axis in sorted(axes_to_trace, reverse=True):
        tensor = np.trace(tensor, axis1=axis, axis2=axis + n)
        n -= 1  # contraction reduces remaining axes

    kept_dim = int(np.prod([dims[i] for i in keep]))
    return tensor.reshape(kept_dim, kept_dim)


def partial_transpose(
    rho: np.ndarray,
    subsystems: Sequence[int],
    dims: Sequence[int] | None = None,
) -> np.ndarray:
    """
    Partial transpose of a multi-qubit density matrix over the listed
    subsystems.
    """
    rho = _state_to_density(rho)
    n = _dims_from_n(rho) if dims is None else len(dims)
    dims = list(dims) if dims is not None else [2] * n

    shape = dims + dims
    tensor = rho.reshape(shape)

    # Swap row/col indices for transposed subsystems
    perm = list(range(2 * n))
    for sub in subsystems:
        perm[sub], perm[sub + n] = perm[sub + n], perm[sub]
    tensor = tensor.transpose(perm)
    return tensor.reshape(rho.shape)


# ---------------------------------------------------------------------------
# Entanglement measures
# ---------------------------------------------------------------------------

_SY = np.array([[0, -1j], [1j, 0]], dtype=complex)


def concurrence(rho_or_state: np.ndarray) -> float:
    """
    Concurrence of a two-qubit mixed state (Wootters 1998).
    Accepts a 4-dim pure state or a 4x4 density matrix.
    """
    rho = _state_to_density(rho_or_state)
    if rho.shape != (4, 4):
        raise ValueError("concurrence requires a two-qubit state")
    Y = np.kron(_SY, _SY)
    rho_tilde = Y @ np.conj(rho) @ Y
    # Eigenvalues of rho * rho_tilde (sorted descending) -> sqrt -> concurrence
    eigvals = np.linalg.eigvals(rho @ rho_tilde)
    eigvals = np.real(eigvals)
    eigvals = np.clip(eigvals, 0.0, None)
    sqrt_eig = np.sort(np.sqrt(eigvals))[::-1]
    c = sqrt_eig[0] - sqrt_eig[1] - sqrt_eig[2] - sqrt_eig[3]
    return float(max(0.0, c))


def negativity(
    rho_or_state: np.ndarray,
    subsystems: Sequence[int] | None = None,
    dims: Sequence[int] | None = None,
) -> float:
    """
    Negativity N(rho) = (||rho^{T_B}||_1 - 1) / 2.

    For an n-qubit state, `subsystems` defines which qubits form the "B" side
    of the bipartition; default is all but the first qubit.
    """
    rho = _state_to_density(rho_or_state)
    n = _dims_from_n(rho) if dims is None else len(dims)
    if subsystems is None:
        subsystems = list(range(1, n))
    rho_pt = partial_transpose(rho, subsystems, dims)
    eigvals = np.linalg.eigvalsh((rho_pt + rho_pt.conj().T) / 2)
    trace_norm = float(np.sum(np.abs(eigvals)))
    return max(0.0, (trace_norm - 1.0) / 2.0)


def logarithmic_negativity(
    rho_or_state: np.ndarray,
    subsystems: Sequence[int] | None = None,
    dims: Sequence[int] | None = None,
) -> float:
    """E_N = log2(||rho^{T_B}||_1)."""
    rho = _state_to_density(rho_or_state)
    n = _dims_from_n(rho) if dims is None else len(dims)
    if subsystems is None:
        subsystems = list(range(1, n))
    rho_pt = partial_transpose(rho, subsystems, dims)
    eigvals = np.linalg.eigvalsh((rho_pt + rho_pt.conj().T) / 2)
    trace_norm = float(np.sum(np.abs(eigvals)))
    return float(np.log2(max(trace_norm, 1e-15)))


def purity(rho_or_state: np.ndarray) -> float:
    rho = _state_to_density(rho_or_state)
    return float(np.real(np.trace(rho @ rho)))


def linear_entropy(rho_or_state: np.ndarray) -> float:
    rho = _state_to_density(rho_or_state)
    d = rho.shape[0]
    return float((d / (d - 1)) * (1.0 - purity(rho))) if d > 1 else 0.0


def von_neumann_entropy(rho_or_state: np.ndarray) -> float:
    rho = _state_to_density(rho_or_state)
    eigvals = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    eigvals = np.clip(np.real(eigvals), 0.0, 1.0)
    s = 0.0
    for ev in eigvals:
        if ev > 1e-12:
            s -= ev * np.log2(ev)
    return float(s)


def mutual_information(
    rho_or_state: np.ndarray,
    subsystem_a: Sequence[int],
    subsystem_b: Sequence[int],
) -> float:
    """I(A:B) = S(A) + S(B) - S(AB)."""
    rho = _state_to_density(rho_or_state)
    rho_a = partial_trace(rho, subsystem_a)
    rho_b = partial_trace(rho, subsystem_b)
    rho_ab = partial_trace(rho, list(subsystem_a) + list(subsystem_b))
    return (
        von_neumann_entropy(rho_a)
        + von_neumann_entropy(rho_b)
        - von_neumann_entropy(rho_ab)
    )


def discord_proxy(
    rho_or_state: np.ndarray,
    subsystem_a: Sequence[int],
    subsystem_b: Sequence[int],
    n_samples: int = 6,
) -> float:
    """
    Lower-bound *proxy* for quantum discord D(A|B).

    Full quantum discord is NP-hard, but for ERH diagnostics we compute

        D_proxy = I(A:B) - max_{sigma-Z basis rotations} J_classical(A|B)

    over a small grid of single-qubit basis rotations on B (polar angle theta,
    phi=0).  Returns 0 if the grid cannot find a classical correlation below
    the mutual information (which should not happen).
    """
    rho = _state_to_density(rho_or_state)
    I_AB = mutual_information(rho, subsystem_a, subsystem_b)

    # Compute classical correlation J := max_{Pi_k on B} [S(A) - sum_k p_k S(rho_A|k)]
    rho_a = partial_trace(rho, subsystem_a)
    S_A = von_neumann_entropy(rho_a)

    if len(subsystem_b) != 1:
        # Only implement single-qubit measurement on B for this proxy.
        # Fall back to mutual information lower bound.
        return max(0.0, I_AB / 2.0)

    q_b = int(subsystem_b[0])
    n = _dims_from_n(rho)
    best_J = -np.inf
    thetas = np.linspace(0, np.pi, n_samples)
    for theta in thetas:
        # Measurement operators in rotated basis on qubit q_b
        # |+theta> = cos(theta/2)|0> + sin(theta/2)|1>
        c = np.cos(theta / 2)
        s = np.sin(theta / 2)
        v0 = np.array([c, s], dtype=complex)
        v1 = np.array([-s, c], dtype=complex)
        projectors = [np.outer(v0, np.conj(v0)), np.outer(v1, np.conj(v1))]

        cond_entropy = 0.0
        for P in projectors:
            # Build full projector P_full on qubit q_b, identity elsewhere
            P_full = np.array([[1.0]], dtype=complex)
            for q in range(n):
                if q == q_b:
                    P_full = np.kron(P, P_full)
                else:
                    P_full = np.kron(np.eye(2, dtype=complex), P_full)
            rho_post = P_full @ rho @ P_full
            p = float(np.real(np.trace(rho_post)))
            if p < 1e-12:
                continue
            rho_post = rho_post / p
            rho_a_post = partial_trace(rho_post, subsystem_a)
            cond_entropy += p * von_neumann_entropy(rho_a_post)

        J = S_A - cond_entropy
        if J > best_J:
            best_J = J
    if best_J == -np.inf:
        return max(0.0, I_AB / 2.0)
    return float(max(0.0, I_AB - best_J))
