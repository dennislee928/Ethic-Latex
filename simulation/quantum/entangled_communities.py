"""
Entangled Moral Communities (§1.1 of QUANTUM_SIMULATION_PLANS.md).

Creates non-local correlations between sub-communities using multipartite
entangled states (Bell, GHZ, W, cluster states) across community partitions.

A *community partition* is a list of lists of qubit indices.  Each community
is prepared in a chosen multipartite entangled state, and then communities are
optionally "stitched" with CNOT-bridges between partitions to model non-local
inter-community echo chamber effects.

Implementation uses pure NumPy state-vector math so the module has no external
quantum dependencies.  Qiskit helpers are provided when qiskit is available.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple, Optional, Dict, Any

import numpy as np

try:  # optional qiskit integration
    from qiskit import QuantumCircuit  # noqa: F401

    _QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    _QISKIT_AVAILABLE = False

__all__ = [
    "bell_pair_state",
    "ghz_state",
    "w_state",
    "cluster_state_1d",
    "build_community_state",
    "echo_chamber_bridge",
    "community_correlation",
    "EntangledCommunityNetwork",
]


# ---------------------------------------------------------------------------
# Elementary multipartite states
# ---------------------------------------------------------------------------

def bell_pair_state(kind: str = "phi_plus") -> np.ndarray:
    """Two-qubit Bell state vector (little-endian qubit ordering)."""
    s = np.zeros(4, dtype=complex)
    inv_sqrt2 = 1.0 / np.sqrt(2.0)
    if kind == "phi_plus":   # (|00> + |11>)/sqrt(2)
        s[0b00] = inv_sqrt2
        s[0b11] = inv_sqrt2
    elif kind == "phi_minus":
        s[0b00] = inv_sqrt2
        s[0b11] = -inv_sqrt2
    elif kind == "psi_plus":  # (|01> + |10>)/sqrt(2)
        s[0b01] = inv_sqrt2
        s[0b10] = inv_sqrt2
    elif kind == "psi_minus":
        s[0b01] = inv_sqrt2
        s[0b10] = -inv_sqrt2
    else:
        raise ValueError(f"unknown Bell kind: {kind}")
    return s


def ghz_state(n: int) -> np.ndarray:
    """n-qubit GHZ state: (|0..0> + |1..1>)/sqrt(2)."""
    if n < 1:
        raise ValueError("n must be >= 1")
    dim = 1 << n
    s = np.zeros(dim, dtype=complex)
    inv_sqrt2 = 1.0 / np.sqrt(2.0)
    s[0] = inv_sqrt2
    s[dim - 1] = inv_sqrt2
    return s


def w_state(n: int) -> np.ndarray:
    """
    n-qubit W state: uniform superposition over single-excitation strings.
    |W_n> = (1/sqrt(n)) * sum_k |0..1_k..0>
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    dim = 1 << n
    s = np.zeros(dim, dtype=complex)
    norm = 1.0 / np.sqrt(n)
    for k in range(n):
        s[1 << k] = norm
    return s


def cluster_state_1d(n: int) -> np.ndarray:
    """
    1D linear cluster state: apply H to each qubit in |0>^n then CZ on every
    nearest-neighbour pair.  Useful for measurement-based morality graphs.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    dim = 1 << n
    state = np.zeros(dim, dtype=complex)
    state[0] = 1.0

    # Apply Hadamard on each qubit
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2.0)
    for q in range(n):
        state = _apply_1q_gate(state, H, q, n)

    # CZ on each nearest-neighbour
    for q in range(n - 1):
        state = _apply_cz(state, q, q + 1, n)
    return state


# ---------------------------------------------------------------------------
# State-vector helpers (little-endian qubit ordering: qubit 0 is least sig. bit)
# ---------------------------------------------------------------------------

def _apply_1q_gate(state: np.ndarray, gate: np.ndarray, q: int, n: int) -> np.ndarray:
    """Apply a 2x2 gate to qubit q of an n-qubit state vector."""
    dim = 1 << n
    out = np.zeros_like(state)
    bit = 1 << q
    for idx in range(dim):
        if idx & bit:
            continue
        i0 = idx
        i1 = idx | bit
        a0, a1 = state[i0], state[i1]
        out[i0] = gate[0, 0] * a0 + gate[0, 1] * a1
        out[i1] = gate[1, 0] * a0 + gate[1, 1] * a1
    return out


def _apply_cz(state: np.ndarray, q0: int, q1: int, n: int) -> np.ndarray:
    """Apply CZ gate between qubits q0, q1 (commutative)."""
    out = state.copy()
    mask = (1 << q0) | (1 << q1)
    for idx in range(1 << n):
        if (idx & mask) == mask:
            out[idx] = -out[idx]
    return out


def _apply_cnot(state: np.ndarray, ctrl: int, tgt: int, n: int) -> np.ndarray:
    out = state.copy()
    cbit = 1 << ctrl
    tbit = 1 << tgt
    dim = 1 << n
    for idx in range(dim):
        if idx & cbit:
            j = idx ^ tbit
            if idx < j:
                out[idx], out[j] = state[j], state[idx]
    return out


# ---------------------------------------------------------------------------
# Community-level builders
# ---------------------------------------------------------------------------

def _embed_state(small: np.ndarray, qubits: Sequence[int], n_total: int) -> np.ndarray:
    """
    Embed a small (k-qubit) state on the specified `qubits` into an n_total-qubit
    register initially in |0...0>.
    """
    k = len(qubits)
    if small.shape[0] != (1 << k):
        raise ValueError("state dimension does not match qubit count")
    dim_total = 1 << n_total
    out = np.zeros(dim_total, dtype=complex)
    for i in range(1 << k):
        # Map local bit-pattern `i` onto the big register.
        big_idx = 0
        for loc_bit in range(k):
            if (i >> loc_bit) & 1:
                big_idx |= 1 << qubits[loc_bit]
        out[big_idx] = small[i]
    return out


def _kron_states(state_a: np.ndarray, qubits_a: Sequence[int],
                 state_b: np.ndarray, qubits_b: Sequence[int],
                 n_total: int) -> np.ndarray:
    """Tensor two sub-system states on disjoint qubit sets into full register."""
    # Build as direct product by summing over computational basis
    dim = 1 << n_total
    out = np.zeros(dim, dtype=complex)
    ka, kb = len(qubits_a), len(qubits_b)
    for ia in range(1 << ka):
        amp_a = state_a[ia]
        if abs(amp_a) < 1e-15:
            continue
        for ib in range(1 << kb):
            amp_b = state_b[ib]
            if abs(amp_b) < 1e-15:
                continue
            big_idx = 0
            for bit in range(ka):
                if (ia >> bit) & 1:
                    big_idx |= 1 << qubits_a[bit]
            for bit in range(kb):
                if (ib >> bit) & 1:
                    big_idx |= 1 << qubits_b[bit]
            out[big_idx] = amp_a * amp_b
    return out


def build_community_state(
    communities: Sequence[Sequence[int]],
    state_kind: str = "ghz",
    n_total: Optional[int] = None,
) -> np.ndarray:
    """
    Build a global state where each community is in its own multipartite
    entangled state and communities are mutually product.

    Parameters
    ----------
    communities : list of lists of ints
        Partitioning of qubit indices into communities.
    state_kind : {"ghz", "w", "bell", "cluster"}, default "ghz"
        Entangled state kind inside each community.  "bell" requires 2-qubit
        communities.
    n_total : int | None
        Total qubit count.  Defaults to max(flatten(communities)) + 1.

    Returns
    -------
    ndarray, shape (2**n_total,)
        Normalised state vector.
    """
    flat = [q for c in communities for q in c]
    if len(set(flat)) != len(flat):
        raise ValueError("communities must be disjoint")
    if n_total is None:
        n_total = max(flat) + 1 if flat else 0

    global_state: Optional[np.ndarray] = None
    used_qubits: List[int] = []

    for community in communities:
        k = len(community)
        if state_kind == "ghz":
            local = ghz_state(k)
        elif state_kind == "w":
            local = w_state(k)
        elif state_kind == "bell":
            if k != 2:
                raise ValueError("bell state requires 2-qubit communities")
            local = bell_pair_state("phi_plus")
        elif state_kind == "cluster":
            local = cluster_state_1d(k)
        else:
            raise ValueError(f"unknown state_kind {state_kind}")
        if global_state is None:
            global_state = _embed_state(local, community, n_total)
            used_qubits = list(community)
        else:
            global_state = _kron_states(
                global_state, used_qubits, local, community, n_total
            )
            used_qubits.extend(community)

    # Fill remaining qubits (not in any community) as |0>.
    if global_state is None:
        dim = 1 << n_total
        global_state = np.zeros(dim, dtype=complex)
        global_state[0] = 1.0

    # Normalise (guard against numerical drift)
    nrm = np.linalg.norm(global_state)
    if nrm > 0:
        global_state = global_state / nrm
    return global_state


def echo_chamber_bridge(
    state: np.ndarray,
    bridges: Sequence[Tuple[int, int]],
    n_total: int,
    gate: str = "cnot",
) -> np.ndarray:
    """
    Add non-local inter-community correlations by applying CNOT / CZ bridges
    between qubits in distinct communities.

    This models an ideological echo chamber: a small subset of qubits from
    one community is entangled with another community, so measuring one
    influences the other.
    """
    out = state.copy()
    for (ctrl, tgt) in bridges:
        if gate == "cnot":
            out = _apply_cnot(out, ctrl, tgt, n_total)
        elif gate == "cz":
            out = _apply_cz(out, ctrl, tgt, n_total)
        else:
            raise ValueError(f"unknown bridge gate {gate}")
    return out


# ---------------------------------------------------------------------------
# Correlation diagnostics
# ---------------------------------------------------------------------------

def community_correlation(
    state: np.ndarray,
    community_a: Sequence[int],
    community_b: Sequence[int],
) -> float:
    """
    Compute <Z_A Z_B> - <Z_A><Z_B> treating Z_A (resp. Z_B) as the parity
    of all qubits in community A (resp. B).  Range [-1, 1].
    """
    dim = state.shape[0]
    n_total = int(np.log2(dim))
    probs = np.abs(state) ** 2
    mask_a = 0
    for q in community_a:
        mask_a |= 1 << q
    mask_b = 0
    for q in community_b:
        mask_b |= 1 << q

    ZA = 0.0
    ZB = 0.0
    ZAZB = 0.0
    for idx in range(dim):
        p = probs[idx]
        if p == 0.0:
            continue
        za = 1 if bin(idx & mask_a).count("1") % 2 == 0 else -1
        zb = 1 if bin(idx & mask_b).count("1") % 2 == 0 else -1
        ZA += p * za
        ZB += p * zb
        ZAZB += p * za * zb
    return float(ZAZB - ZA * ZB)


# ---------------------------------------------------------------------------
# Convenience network class
# ---------------------------------------------------------------------------

class EntangledCommunityNetwork:
    """High-level helper: communities + bridges + analysis."""

    def __init__(
        self,
        communities: Sequence[Sequence[int]],
        state_kind: str = "ghz",
        bridges: Optional[Sequence[Tuple[int, int]]] = None,
        bridge_gate: str = "cnot",
        n_total: Optional[int] = None,
    ) -> None:
        self.communities = [list(c) for c in communities]
        flat = [q for c in self.communities for q in c]
        self.n_total = n_total or (max(flat) + 1 if flat else 0)
        self.state_kind = state_kind
        self.bridges = list(bridges or [])
        self.bridge_gate = bridge_gate

    def build_state(self) -> np.ndarray:
        s = build_community_state(self.communities, self.state_kind, self.n_total)
        if self.bridges:
            s = echo_chamber_bridge(s, self.bridges, self.n_total, self.bridge_gate)
        return s

    def analyse(self) -> Dict[str, Any]:
        state = self.build_state()
        corrs: Dict[Tuple[int, int], float] = {}
        for i in range(len(self.communities)):
            for j in range(i + 1, len(self.communities)):
                corrs[(i, j)] = community_correlation(
                    state, self.communities[i], self.communities[j]
                )
        return {
            "state": state,
            "inter_community_correlations": corrs,
            "probabilities": np.abs(state) ** 2,
        }
