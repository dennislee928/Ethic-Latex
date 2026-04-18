"""
Open-system evolution via the Lindblad master equation (§3.3) plus a
time-dependent Hamiltonian integrator (§3.2).

    drho/dt = -i[H(t), rho] + sum_k gamma_k ( L_k rho L_k^\dagger
                                             - 0.5 {L_k^\dagger L_k, rho} )

We use SciPy when available for a high-accuracy integrator, and fall back to
a 4th-order Runge-Kutta implementation otherwise.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

try:
    from scipy.integrate import solve_ivp

    _SCIPY_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    _SCIPY_AVAILABLE = False

__all__ = [
    "commutator",
    "lindblad_rhs",
    "evolve_unitary",
    "evolve_lindblad",
    "time_dependent_evolution",
    "kraus_amplitude_damping",
    "kraus_depolarising",
    "apply_kraus",
]


def commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return A @ B - B @ A


def anticommutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return A @ B + B @ A


def lindblad_rhs(
    rho: np.ndarray,
    H: np.ndarray,
    jump_ops: Sequence[np.ndarray],
    rates: Sequence[float],
) -> np.ndarray:
    """Right-hand side of the Lindblad equation at fixed H."""
    drho = -1j * commutator(H, rho)
    for L, g in zip(jump_ops, rates):
        Ld = L.conj().T
        drho += g * (L @ rho @ Ld - 0.5 * anticommutator(Ld @ L, rho))
    return drho


# ---------------------------------------------------------------------------
# Integrators
# ---------------------------------------------------------------------------

def _rk4_step(rho: np.ndarray, H_t: np.ndarray, jumps: Sequence[np.ndarray],
              rates: Sequence[float], dt: float) -> np.ndarray:
    k1 = lindblad_rhs(rho, H_t, jumps, rates)
    k2 = lindblad_rhs(rho + 0.5 * dt * k1, H_t, jumps, rates)
    k3 = lindblad_rhs(rho + 0.5 * dt * k2, H_t, jumps, rates)
    k4 = lindblad_rhs(rho + dt * k3, H_t, jumps, rates)
    return rho + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def evolve_unitary(
    H: np.ndarray,
    state: np.ndarray,
    t: float,
) -> np.ndarray:
    """Exact unitary evolution via matrix exponentiation (state vector)."""
    # eig-decomposition is numerically stable for Hermitian H
    H = (H + H.conj().T) / 2
    w, V = np.linalg.eigh(H)
    phase = np.exp(-1j * w * t)
    return V @ (phase * (V.conj().T @ state))


def evolve_lindblad(
    H: np.ndarray,
    rho0: np.ndarray,
    jump_ops: Sequence[np.ndarray],
    rates: Sequence[float],
    t_span: Tuple[float, float],
    n_steps: int = 200,
    method: str = "auto",
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Integrate Lindblad equation with a time-independent Hamiltonian.

    Returns (times, rhos) where rhos has shape (n_steps + 1, dim, dim).
    """
    t0, t1 = t_span
    times = np.linspace(t0, t1, n_steps + 1)

    if rho0.ndim == 1:
        rho0 = np.outer(rho0, np.conj(rho0))

    use_scipy = _SCIPY_AVAILABLE and method in ("auto", "scipy")
    if use_scipy:
        d = rho0.shape[0]

        def rhs(_t, y):
            rho = y.reshape(d, d)
            return lindblad_rhs(rho, H, jump_ops, rates).reshape(-1)

        sol = solve_ivp(
            rhs, t_span, rho0.reshape(-1), t_eval=times, rtol=1e-8, atol=1e-10
        )
        rhos = np.array([sol.y[:, i].reshape(d, d) for i in range(sol.y.shape[1])])
        return times, rhos

    # RK4 fallback
    dt = (t1 - t0) / n_steps
    rho = rho0.astype(complex).copy()
    rhos = [rho.copy()]
    for _ in range(n_steps):
        rho = _rk4_step(rho, H, jump_ops, rates, dt)
        rhos.append(rho.copy())
    return times, np.array(rhos)


def time_dependent_evolution(
    H_func: Callable[[float], np.ndarray],
    rho0: np.ndarray,
    jump_ops: Sequence[np.ndarray],
    rates: Sequence[float],
    t_span: Tuple[float, float],
    n_steps: int = 400,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Integrate Lindblad with time-dependent Hamiltonian H(t).
    Uses RK4 on the density matrix.
    """
    t0, t1 = t_span
    times = np.linspace(t0, t1, n_steps + 1)
    if rho0.ndim == 1:
        rho0 = np.outer(rho0, np.conj(rho0))

    rho = rho0.astype(complex).copy()
    rhos = [rho.copy()]
    dt = (t1 - t0) / n_steps
    for step in range(n_steps):
        t = times[step]
        H1 = H_func(t)
        H2 = H_func(t + 0.5 * dt)
        H3 = H_func(t + dt)
        k1 = lindblad_rhs(rho, H1, jump_ops, rates)
        k2 = lindblad_rhs(rho + 0.5 * dt * k1, H2, jump_ops, rates)
        k3 = lindblad_rhs(rho + 0.5 * dt * k2, H2, jump_ops, rates)
        k4 = lindblad_rhs(rho + dt * k3, H3, jump_ops, rates)
        rho = rho + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        rhos.append(rho.copy())
    return times, np.array(rhos)


# ---------------------------------------------------------------------------
# Kraus operator channels (for simple noise application)
# ---------------------------------------------------------------------------

def kraus_amplitude_damping(gamma: float) -> List[np.ndarray]:
    """Single-qubit amplitude damping channel."""
    if not 0.0 <= gamma <= 1.0:
        raise ValueError("gamma in [0,1]")
    K0 = np.array([[1.0, 0.0], [0.0, np.sqrt(1.0 - gamma)]], dtype=complex)
    K1 = np.array([[0.0, np.sqrt(gamma)], [0.0, 0.0]], dtype=complex)
    return [K0, K1]


def kraus_depolarising(p: float) -> List[np.ndarray]:
    """Single-qubit depolarising channel with total error probability p."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("p in [0,1]")
    s = np.sqrt(p / 3.0)
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    return [np.sqrt(1 - p) * I, s * X, s * Y, s * Z]


def apply_kraus(rho: np.ndarray, kraus: Sequence[np.ndarray]) -> np.ndarray:
    """rho -> sum K_i rho K_i^dagger."""
    out = np.zeros_like(rho, dtype=complex)
    for K in kraus:
        out = out + K @ rho @ K.conj().T
    return out
