"""
Topological moral phases (§3.4).

Provides:
    * A Kitaev-chain-style Hamiltonian (1D p-wave superconductor / SSH-like)
    * Winding number and Berry phase computation in momentum space
    * Classification of trivial vs topological phases

We model the chain in momentum space as a 2x2 Bloch Hamiltonian
    H(k) = d_x(k) sigma_x + d_y(k) sigma_y + d_z(k) sigma_z
The winding number of (d_x, d_y) around the origin (when d_z=0) gives the
1D topological invariant.  For the Kitaev chain (or the Su-Schrieffer-Heeger
model) this is 0 in the trivial phase and 1 in the topological phase.
"""

from __future__ import annotations

from typing import Callable, Tuple

import numpy as np

__all__ = [
    "kitaev_bloch_hamiltonian",
    "ssh_bloch_hamiltonian",
    "winding_number",
    "berry_phase",
    "kitaev_real_space_hamiltonian",
    "classify_phase",
]


def kitaev_bloch_hamiltonian(
    k: float,
    mu: float = 0.0,
    t: float = 1.0,
    delta: float = 1.0,
) -> np.ndarray:
    """
    Kitaev p-wave chain 2x2 Bloch Hamiltonian:
        H(k) = -(2t cos k + mu) sigma_z + 2 Delta sin k sigma_y
    """
    s_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    s_z = np.array([[1, 0], [0, -1]], dtype=complex)
    return (-(2.0 * t * np.cos(k) + mu)) * s_z + (2.0 * delta * np.sin(k)) * s_y


def ssh_bloch_hamiltonian(k: float, v: float = 1.0, w: float = 0.5) -> np.ndarray:
    """
    Su-Schrieffer-Heeger 2x2 Bloch Hamiltonian:
        H(k) = (v + w cos k) sigma_x + w sin k sigma_y
    """
    s_x = np.array([[0, 1], [1, 0]], dtype=complex)
    s_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    return (v + w * np.cos(k)) * s_x + (w * np.sin(k)) * s_y


def _d_vector(H_k: np.ndarray) -> Tuple[float, float, float]:
    """Extract (d_x, d_y, d_z) from a 2x2 Bloch Hamiltonian."""
    dx = float(np.real(H_k[0, 1] + H_k[1, 0]) / 2.0)
    dy = float(np.real(1j * (H_k[0, 1] - H_k[1, 0])) / 2.0)
    dz = float(np.real(H_k[0, 0] - H_k[1, 1]) / 2.0)
    return dx, dy, dz


def winding_number(
    bloch_fn: Callable[[float], np.ndarray],
    n_points: int = 400,
) -> int:
    """
    Winding number of (d_x, d_y) around the origin as k sweeps [-pi, pi].

    For SSH / Kitaev-with-chiral-symmetry the winding jumps between 0 and 1
    when crossing the topological phase transition.  Returns rounded integer.
    """
    # Sample k on a closed loop (duplicate endpoint)
    ks = np.linspace(-np.pi, np.pi, n_points + 1)
    xs = []
    ys = []
    for k in ks:
        H = bloch_fn(k)
        dx, dy, _dz = _d_vector(H)
        xs.append(dx)
        ys.append(dy)
    xs = np.array(xs)
    ys = np.array(ys)

    # Accumulate phase differences using atan2 of cross/dot products to avoid
    # branch-cut issues of np.unwrap.
    total = 0.0
    for i in range(n_points):
        x1, y1 = xs[i], ys[i]
        x2, y2 = xs[i + 1], ys[i + 1]
        cross = x1 * y2 - y1 * x2
        dot = x1 * x2 + y1 * y2
        # Avoid zero radius (would be on gap closure)
        if abs(cross) < 1e-14 and abs(dot) < 1e-14:
            continue
        total += np.arctan2(cross, dot)
    return int(round(total / (2 * np.pi)))


def berry_phase(
    bloch_fn: Callable[[float], np.ndarray],
    n_points: int = 400,
    band: int = 0,
) -> float:
    """
    Discrete Berry phase of `band` (0 = lower) across the Brillouin zone
    [-pi, pi], using the Wilson-loop formulation.
    """
    ks = np.linspace(-np.pi, np.pi, n_points, endpoint=False)
    eigenvectors = []
    for k in ks:
        H = bloch_fn(k)
        H = (H + H.conj().T) / 2
        w, v = np.linalg.eigh(H)
        eigenvectors.append(v[:, band])

    prod = 1.0 + 0.0j
    for i in range(len(ks)):
        u_i = eigenvectors[i]
        u_j = eigenvectors[(i + 1) % len(ks)]
        ov = np.vdot(u_i, u_j)
        if ov != 0:
            prod *= ov / abs(ov)
    return float(-np.angle(prod))


def kitaev_real_space_hamiltonian(
    n: int,
    mu: float = 0.0,
    t: float = 1.0,
    delta: float = 1.0,
) -> np.ndarray:
    """
    Real-space BdG Hamiltonian for an open Kitaev chain (2n x 2n matrix
    in Nambu basis c_i, c_i^dagger).  Useful to visualise Majorana zero modes.
    """
    dim = 2 * n
    H = np.zeros((dim, dim), dtype=complex)
    for i in range(n):
        H[i, i] = -mu
        H[i + n, i + n] = mu
    for i in range(n - 1):
        # Hopping
        H[i, i + 1] += -t
        H[i + 1, i] += -t
        H[i + n, i + 1 + n] += t
        H[i + 1 + n, i + n] += t
        # Pairing (p-wave)
        H[i, i + 1 + n] += delta
        H[i + 1 + n, i] += np.conj(delta)
        H[i + 1, i + n] += -delta
        H[i + n, i + 1] += -np.conj(delta)
    return (H + H.conj().T) / 2  # enforce Hermiticity


def classify_phase(
    bloch_fn: Callable[[float], np.ndarray],
    n_points: int = 400,
) -> str:
    """Return 'trivial' or 'topological' based on winding number."""
    w = winding_number(bloch_fn, n_points)
    return "topological" if abs(w) >= 1 else "trivial"
