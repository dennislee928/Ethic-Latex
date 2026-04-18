"""
Noise model hooks (§2.4) for the quantum ethical pipeline.

Lightweight, vendor-agnostic Kraus/Lindblad noise primitives plus a multi-qubit
noise applicator.  Qiskit noise models are wrapped when available.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

from . import lindblad as _lb

try:
    from qiskit_aer.noise import NoiseModel, depolarizing_error, amplitude_damping_error

    _AER_NOISE = True
except Exception:  # pragma: no cover
    _AER_NOISE = False

__all__ = [
    "single_qubit_lindblad_ops",
    "multi_qubit_depolarising_kraus",
    "apply_noise_to_density",
    "apply_single_qubit_noise",
    "build_aer_noise_model",
]


def single_qubit_lindblad_ops(
    qubit: int,
    n_total: int,
    amp_damp: float = 0.0,
    dephasing: float = 0.0,
) -> List[Tuple[np.ndarray, float]]:
    """
    Build Lindblad jump operators for a single qubit embedded in n_total qubits.

    Returns list of (operator, rate) pairs.  amp_damp is gamma1, dephasing is
    gamma_phi.  Operators use little-endian qubit ordering.
    """
    ops: List[Tuple[np.ndarray, float]] = []
    sigma_minus_local = np.array([[0, 1], [0, 0]], dtype=complex)
    sigma_z_local = np.array([[1, 0], [0, -1]], dtype=complex)

    if amp_damp > 0.0:
        L = _embed(sigma_minus_local, qubit, n_total)
        ops.append((L, amp_damp))
    if dephasing > 0.0:
        L = _embed(sigma_z_local, qubit, n_total)
        ops.append((L, dephasing))
    return ops


def _embed(op_local: np.ndarray, q: int, n: int) -> np.ndarray:
    I = np.eye(2, dtype=complex)
    out = np.array([[1.0]], dtype=complex)
    for j in reversed(range(n)):  # little-endian
        out = np.kron(out, op_local if j == q else I)
    return out


def multi_qubit_depolarising_kraus(
    n: int,
    p: float,
) -> List[np.ndarray]:
    """
    Product of independent single-qubit depolarising channels (approximation:
    apply a single global channel that is the weighted mixture).  For small n
    we return the exact tensor-product Kraus set.
    """
    if n < 1:
        raise ValueError("n >= 1")
    per_qubit = _lb.kraus_depolarising(p)
    kraus = [np.array([[1.0]], dtype=complex)]
    for _ in range(n):
        new = []
        for k in kraus:
            for kk in per_qubit:
                new.append(np.kron(k, kk))
        kraus = new
    return kraus


def apply_single_qubit_noise(
    rho: np.ndarray,
    qubit: int,
    channel: str,
    strength: float,
    n_total: Optional[int] = None,
) -> np.ndarray:
    """
    Apply a single-qubit channel to a multi-qubit density matrix.

    channel in {"depolarising", "amplitude_damping", "dephasing"}.
    """
    dim = rho.shape[0]
    if n_total is None:
        n_total = int(round(np.log2(dim)))
    if channel == "depolarising":
        local_kraus = _lb.kraus_depolarising(strength)
    elif channel == "amplitude_damping":
        local_kraus = _lb.kraus_amplitude_damping(strength)
    elif channel == "dephasing":
        # pure dephasing: K0=sqrt(1-p) I, K1=sqrt(p) Z
        I = np.eye(2, dtype=complex)
        Z = np.array([[1, 0], [0, -1]], dtype=complex)
        local_kraus = [np.sqrt(1 - strength) * I, np.sqrt(strength) * Z]
    else:
        raise ValueError(f"unknown channel {channel}")

    # Embed each Kraus operator into full space
    embedded = [_embed(K, qubit, n_total) for K in local_kraus]
    return _lb.apply_kraus(rho, embedded)


def apply_noise_to_density(
    rho: np.ndarray,
    channels: Iterable[Tuple[int, str, float]],
) -> np.ndarray:
    """
    Apply a sequence of per-qubit noise channels to a density matrix.

    Each channel is (qubit_index, channel_name, strength).
    """
    for q, name, s in channels:
        rho = apply_single_qubit_noise(rho, q, name, s)
    return rho


def build_aer_noise_model(
    single_qubit_depol: float = 0.0,
    two_qubit_depol: float = 0.0,
    amp_damp: float = 0.0,
    gate_times_ns: Optional[dict] = None,
):
    """Build a qiskit_aer NoiseModel (returns None if qiskit_aer is unavailable)."""
    if not _AER_NOISE:
        return None
    model = NoiseModel()
    if single_qubit_depol > 0.0:
        err1 = depolarizing_error(single_qubit_depol, 1)
        model.add_all_qubit_quantum_error(err1, ["u1", "u2", "u3", "rx", "ry", "rz", "h", "x", "y", "z", "s", "sdg", "t"])
    if two_qubit_depol > 0.0:
        err2 = depolarizing_error(two_qubit_depol, 2)
        model.add_all_qubit_quantum_error(err2, ["cx", "cz"])
    if amp_damp > 0.0:
        err_ad = amplitude_damping_error(amp_damp)
        model.add_all_qubit_quantum_error(err_ad, ["u1", "u2", "u3", "rx", "ry", "rz", "h"])
    return model
