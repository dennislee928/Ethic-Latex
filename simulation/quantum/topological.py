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

from typing import Callable, Optional, Tuple

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
    plane: Optional[str] = None,
) -> int:
    """
    Winding number of a two-component component of the d-vector around the
    origin as k sweeps [-pi, pi].

    `plane` selects which two d-components to use:
        - "xy"  : (d_x, d_y)   (e.g. SSH with chiral symmetry)
        - "yz"  : (d_y, d_z)   (e.g. Kitaev chain)
        - "xz"  : (d_x, d_z)
        - None  : auto-detect the plane whose components vary the most and
                  whose third component stays closest to zero.
    """
    ks = np.linspace(-np.pi, np.pi, n_points + 1)
    dx = np.zeros(n_points + 1)
    dy = np.zeros(n_points + 1)
    dz = np.zeros(n_points + 1)
    for i, k in enumerate(ks):
        H = bloch_fn(k)
        a, b, c = _d_vector(H)
        dx[i], dy[i], dz[i] = a, b, c

    if plane is None:
        # pick the plane in which the third component has the smallest max|.|
        candidates = [
            ("xy", np.max(np.abs(dz)), dx, dy),
            ("yz", np.max(np.abs(dx)), dy, dz),
            ("xz", np.max(np.abs(dy)), dx, dz),
        ]
        # pick plane with smallest out-of-plane component magnitude
        candidates.sort(key=lambda t: t[1])
        _, _, a, b = candidates[0]
    else:
        mapping = {"xy": (dx, dy), "yz": (dy, dz), "xz": (dx, dz)}
        if plane not in mapping:
            raise ValueError(f"unknown plane {plane}")
        a, b = mapping[plane]

    total = 0.0
    for i in range(n_points):
        x1, y1 = a[i], b[i]
        x2, y2 = a[i + 1], b[i + 1]
        cross = x1 * y2 - y1 * x2
        dot = x1 * x2 + y1 * y2
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
    plane: Optional[str] = None,
) -> str:
    """Return 'trivial' or 'topological' based on winding number."""
    w = winding_number(bloch_fn, n_points, plane=plane)
    return "topological" if abs(w) >= 1 else "trivial"
