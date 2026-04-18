"""
Quantum Machine Learning for ERH parameter discovery (§1.3).

Implements:
    * A lightweight Variational Quantum Eigensolver (VQE) that finds the
      ground state of a NumPy Hamiltonian using a hardware-efficient ansatz
      built in pure NumPy.  Uses scipy.optimize.minimize if SciPy is available,
      otherwise a finite-difference gradient descent.

    * A small Quantum Neural Network (QNN) style fitter that optimises the
      coupling constants J_ij of an Ising / Heisenberg Hamiltonian so that its
      ground-state expectation values match a target data vector.

Both tools are purely classical simulations of the quantum routines (no qiskit
or pennylane required), so they work in any environment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

from .heisenberg import build_xyz_hamiltonian, _embed_one_qubit

try:
    from scipy.optimize import minimize

    _SCIPY_OPT = True
except Exception:  # pragma: no cover
    _SCIPY_OPT = False


__all__ = [
    "hardware_efficient_ansatz",
    "expectation",
    "vqe_ground_state",
    "fit_ising_couplings",
]


# ---------------------------------------------------------------------------
# Ansatz
# ---------------------------------------------------------------------------

def _ry_gate(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2.0), np.sin(theta / 2.0)
    return np.array([[c, -s], [s, c]], dtype=complex)


def _cnot_matrix(n: int, ctrl: int, tgt: int) -> np.ndarray:
    dim = 1 << n
    M = np.zeros((dim, dim), dtype=complex)
    cbit, tbit = 1 << ctrl, 1 << tgt
    for idx in range(dim):
        j = idx ^ tbit if (idx & cbit) else idx
        M[j, idx] = 1.0
    return M


def _apply_single_qubit(state: np.ndarray, gate: np.ndarray, q: int, n: int) -> np.ndarray:
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


def hardware_efficient_ansatz(
    n_qubits: int,
    params: np.ndarray,
    reps: int = 2,
) -> np.ndarray:
    """
    Build a state |psi(params)> using an RY + linear-CNOT ansatz.
    Parameter count = n_qubits * (reps + 1).
    """
    expected = n_qubits * (reps + 1)
    if params.shape[0] != expected:
        raise ValueError(
            f"params length {params.shape[0]} != expected {expected}"
        )
    state = np.zeros(1 << n_qubits, dtype=complex)
    state[0] = 1.0
    p_idx = 0
    for r in range(reps + 1):
        for q in range(n_qubits):
            state = _apply_single_qubit(state, _ry_gate(params[p_idx]), q, n_qubits)
            p_idx += 1
        if r < reps:
            # Linear CNOT entangling layer
            for q in range(n_qubits - 1):
                state = _cnot_matrix(n_qubits, q, q + 1) @ state
    return state


# ---------------------------------------------------------------------------
# Expectation + VQE
# ---------------------------------------------------------------------------

def expectation(state: np.ndarray, H: np.ndarray) -> float:
    return float(np.real(np.conj(state) @ (H @ state)))


def vqe_ground_state(
    H: np.ndarray,
    n_qubits: int,
    reps: int = 2,
    maxiter: int = 200,
    seed: Optional[int] = None,
) -> dict:
    """
    Variational eigensolver: returns {'energy', 'params', 'state', 'converged'}.

    The optimiser minimises <psi(theta)|H|psi(theta)> where |psi> is the
    hardware-efficient ansatz above.
    """
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(0.0, 2 * np.pi, size=n_qubits * (reps + 1))

    def cost(x: np.ndarray) -> float:
        state = hardware_efficient_ansatz(n_qubits, x, reps=reps)
        return expectation(state, H)

    if _SCIPY_OPT:
        res = minimize(cost, x0, method="COBYLA", options={"maxiter": maxiter})
        params = res.x
        energy = float(res.fun)
        converged = bool(res.success)
    else:
        # Gradient-free finite-difference descent
        params = x0.copy()
        energy = cost(params)
        eps = 1e-2
        lr = 0.1
        converged = False
        for _ in range(maxiter):
            grad = np.zeros_like(params)
            for k in range(len(params)):
                e1 = params.copy()
                e1[k] += eps
                e2 = params.copy()
                e2[k] -= eps
                grad[k] = (cost(e1) - cost(e2)) / (2 * eps)
            new_params = params - lr * grad
            new_energy = cost(new_params)
            if new_energy >= energy - 1e-8:
                lr *= 0.5
                if lr < 1e-6:
                    converged = True
                    break
                continue
            params, energy = new_params, new_energy

    state = hardware_efficient_ansatz(n_qubits, params, reps=reps)
    return {
        "energy": float(energy),
        "params": params,
        "state": state,
        "converged": converged,
    }


# ---------------------------------------------------------------------------
# QNN-style parameter discovery: fit J_ij to target data
# ---------------------------------------------------------------------------

def _local_Z_expectations(state: np.ndarray, n: int) -> np.ndarray:
    """Return <Z_i> for each qubit i."""
    probs = np.abs(state) ** 2
    expvals = np.zeros(n)
    for i in range(n):
        bit = 1 << i
        for idx in range(len(state)):
            expvals[i] += probs[idx] * (1 if (idx & bit) == 0 else -1)
    return expvals


def fit_ising_couplings(
    target_z: np.ndarray,
    n_qubits: int,
    initial_J: Optional[np.ndarray] = None,
    reps: int = 1,
    maxiter: int = 60,
    seed: Optional[int] = None,
    topology: str = "linear",
) -> dict:
    """
    Given a target vector of single-qubit <Z_i> measurements, find an
    Ising / Heisenberg coupling matrix J_ij (symmetric, zero diagonal) whose
    ground state reproduces those expectation values as closely as possible.

    Returns {'J': J_matrix, 'loss': final_loss, 'state': ground_state}.
    """
    rng = np.random.default_rng(seed)
    if initial_J is None:
        initial_J = rng.uniform(-0.5, 0.5, size=(n_qubits, n_qubits))
        initial_J = 0.5 * (initial_J + initial_J.T)
        np.fill_diagonal(initial_J, 0.0)

    # Flatten upper triangle
    def flatten(J: np.ndarray) -> np.ndarray:
        vals = []
        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                vals.append(J[i, j])
        return np.array(vals)

    def unflatten(flat: np.ndarray) -> np.ndarray:
        J = np.zeros((n_qubits, n_qubits))
        k = 0
        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                J[i, j] = flat[k]
                J[j, i] = flat[k]
                k += 1
        return J

    def ground_z(flat_J: np.ndarray) -> np.ndarray:
        J = unflatten(flat_J)
        # Build Heisenberg-like Hamiltonian with Jz only (Ising) and weak fields
        edges = [(i, j) for i in range(n_qubits) for j in range(i + 1, n_qubits)]
        H = np.zeros((1 << n_qubits, 1 << n_qubits), dtype=complex)
        _I = np.eye(2, dtype=complex)
        _Z = np.array([[1, 0], [0, -1]], dtype=complex)
        for (i, j) in edges:
            mats = [_I] * n_qubits
            mats[i] = _Z
            mats[j] = _Z
            # little-endian Kronecker
            big = np.array([[1.0]], dtype=complex)
            for k in reversed(range(n_qubits)):
                big = np.kron(big, mats[k])
            H += J[i, j] * big
        # add a small transverse field so ground state is not trivially product
        _X = np.array([[0, 1], [1, 0]], dtype=complex)
        for q in range(n_qubits):
            H += 0.25 * _embed_one_qubit(_X, q, n_qubits)
        H = (H + H.conj().T) / 2
        _, eigvecs = np.linalg.eigh(H)
        return _local_Z_expectations(eigvecs[:, 0], n_qubits)

    def loss(flat_J: np.ndarray) -> float:
        pred = ground_z(flat_J)
        return float(np.sum((pred - target_z) ** 2))

    flat0 = flatten(initial_J)

    if _SCIPY_OPT:
        res = minimize(loss, flat0, method="Nelder-Mead",
                       options={"maxiter": maxiter, "fatol": 1e-5, "xatol": 1e-4})
        flat_opt = res.x
        final_loss = float(res.fun)
    else:
        flat = flat0.copy()
        final_loss = loss(flat)
        lr = 0.05
        eps = 1e-2
        for _ in range(maxiter):
            grad = np.zeros_like(flat)
            for k in range(len(flat)):
                a = flat.copy()
                a[k] += eps
                b = flat.copy()
                b[k] -= eps
                grad[k] = (loss(a) - loss(b)) / (2 * eps)
            new = flat - lr * grad
            nl = loss(new)
            if nl >= final_loss - 1e-8:
                lr *= 0.5
                if lr < 1e-6:
                    break
                continue
            flat, final_loss = new, nl
        flat_opt = flat

    J_opt = unflatten(flat_opt)
    pred_z = ground_z(flat_opt)
    return {
        "J": J_opt,
        "loss": final_loss,
        "predicted_z": pred_z,
        "target_z": np.asarray(target_z),
    }
