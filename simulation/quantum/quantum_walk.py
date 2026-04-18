"""
Quantum Random Walk for Opinion Diffusion (Cancel Culture / Viral Moral Panic).

Classical random walk diffuses as O(√t); quantum walk diffuses as O(t).
Models the rapid spread of moral judgment in social networks (e.g. cancel culture).
"""

from typing import Tuple, Optional, List
import numpy as np


def _hadamard_1d() -> np.ndarray:
    """2x2 Hadamard gate."""
    return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


def quantum_walk_step(
    state: np.ndarray,
    n_sites: int,
    coin_bias: float = 0.5,
) -> np.ndarray:
    """
    Single step of Hadamard quantum walk on a line.

    Parameters
    ----------
    state : ndarray, shape (2 * n_sites,)
        Combined position-coin state (position 0..n_sites-1, coin 0 or 1).
    n_sites : int
        Number of sites (graph nodes).
    coin_bias : float, default=0.5
        Bias toward left (0) vs right (1) movement. 0.5 = unbiased.

    Returns
    -------
    ndarray
        New state after one step.
    """
    H = _hadamard_1d() if abs(coin_bias - 0.5) < 1e-9 else np.array([
        [np.sqrt(coin_bias), np.sqrt(1 - coin_bias)],
        [np.sqrt(1 - coin_bias), -np.sqrt(coin_bias)],
    ], dtype=complex)
    new_state = np.zeros_like(state)
    for p in range(n_sites):
        for c in range(2):
            idx = p * 2 + c
            amp = state[idx]
            if abs(amp) < 1e-15:
                continue
            for cn in range(2):
                dest = p + (1 if cn == 1 else -1)
                if 0 <= dest < n_sites:
                    new_state[dest * 2 + cn] += H[cn, c] * amp
    return new_state


def quantum_walk_propagate(
    n_sites: int = 31,
    steps: int = 10,
    initial_site: Optional[int] = None,
    coin_bias: float = 0.5,
    seed: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Propagate quantum walk and return position probability distribution.

    Parameters
    ----------
    n_sites : int, default=31
        Number of sites on the line.
    steps : int, default=10
        Number of walk steps.
    initial_site : int | None, default=None
        Initial position. If None, center.
    coin_bias : float, default=0.5
        Coin bias.
    seed : int | None, default=None
        Random seed (unused for unitary evolution).

    Returns
    -------
    Tuple[ndarray, ndarray]
        (position_probs, timesteps) - prob[i,t] = P(position=i at step t)
    """
    if initial_site is None:
        initial_site = n_sites // 2
    state = np.zeros(2 * n_sites, dtype=complex)
    state[initial_site * 2] = 1.0  # |position, coin=0⟩

    probs = np.zeros((n_sites, steps + 1))
    probs[initial_site, 0] = 1.0

    for t in range(1, steps + 1):
        state = quantum_walk_step(state, n_sites, coin_bias)
        for p in range(n_sites):
            probs[p, t] = float(np.abs(state[p * 2]) ** 2 + np.abs(state[p * 2 + 1]) ** 2)

    return probs, np.arange(steps + 1)


def diffusion_spread(
    n_sites: int = 31,
    steps: int = 20,
    classical: bool = False,
    seed: Optional[int] = None,
) -> Tuple[float, float]:
    """
    Compare classical vs quantum diffusion spread (std of distribution).

    Classical: std ~ O(√t)
    Quantum: std ~ O(t)

    Parameters
    ----------
    n_sites : int
    steps : int
    classical : bool
        If True, simulate classical random walk (binomial).
    seed : int | None

    Returns
    -------
    Tuple[float, float]
        (final_std, spread_at_last_step)
    """
    rng = np.random.default_rng(seed)
    center = n_sites // 2
    if classical:
        pos = center
        positions = [pos]
        for _ in range(steps - 1):
            pos += 1 if rng.random() > 0.5 else -1
            pos = max(0, min(n_sites - 1, pos))
            positions.append(pos)
        probs = np.zeros((n_sites, steps))
        for t, p in enumerate(positions):
            probs[p, t] = 1.0
        final_dist = np.sum(probs, axis=1) / steps
    else:
        probs, _ = quantum_walk_propagate(n_sites, steps, initial_site=center)
        final_dist = probs[:, -1]
    x = np.arange(n_sites)
    mean = np.sum(x * final_dist) / (np.sum(final_dist) + 1e-15)
    std = np.sqrt(np.sum((x - mean) ** 2 * final_dist) / (np.sum(final_dist) + 1e-15))
    return float(std), float(np.max(final_dist))


def simulate_cancel_culture_spread(
    n_agents: int = 50,
    steps: int = 15,
    initial_infected: int = 1,
    quantum: bool = True,
    seed: Optional[int] = None,
) -> dict:
    """
    Simulate opinion/moral panic spread (cancel culture analogy).

    Uses quantum walk for O(t) diffusion when quantum=True,
    classical for O(√t) when quantum=False.

    Returns
    -------
    dict
        - spread_at_step: list of std at each step
        - infected_fraction: fraction of agents with non-negligible probability
        - quantum: bool
    """
    if quantum:
        probs, timesteps = quantum_walk_propagate(
            n_sites=n_agents,
            steps=steps,
            initial_site=min(initial_infected, n_agents - 1),
            seed=seed,
        )
        spread_at_step = []
        for t in range(steps + 1):
            dist = probs[:, t]
            x = np.arange(n_agents)
            mean = np.sum(x * dist) / (np.sum(dist) + 1e-15)
            std = np.sqrt(np.sum((x - mean) ** 2 * dist) / (np.sum(dist) + 1e-15))
            spread_at_step.append(float(std))
        infected_fraction = np.sum(probs[:, -1] > 0.01) / n_agents
    else:
        rng = np.random.default_rng(seed)
        positions = [np.zeros(n_agents) for _ in range(initial_infected)]
        for i in range(initial_infected):
            p = min(i, n_agents - 1)
            positions[i][p] = 1.0
        # Simple classical diffusion: each step, each agent passes to neighbors
        state = np.zeros(n_agents)
        for i in range(initial_infected):
            state += positions[i]
        state /= initial_infected
        spread_at_step = []
        for _ in range(steps + 1):
            x = np.arange(n_agents)
            mean = np.sum(x * state) / (np.sum(state) + 1e-15)
            std = np.sqrt(np.sum((x - mean) ** 2 * state) / (np.sum(state) + 1e-15))
            spread_at_step.append(float(std))
            # Diffusion step
            new_state = np.zeros_like(state)
            for i in range(n_agents):
                if i > 0:
                    new_state[i - 1] += 0.5 * state[i]
                if i < n_agents - 1:
                    new_state[i + 1] += 0.5 * state[i]
            state = new_state
        infected_fraction = np.sum(state > 0.01) / n_agents

    return {
        "spread_at_step": spread_at_step,
        "infected_fraction": float(infected_fraction),
        "quantum": quantum,
    }


# ---------------------------------------------------------------------------
# Coined Quantum Walk on an arbitrary (belief) graph  --  §1.2 of plans
# ---------------------------------------------------------------------------

from typing import Dict


class GraphQuantumWalk:
    """
    Szegedy-style coined quantum walk on a graph representing the "belief space"
    of moral agents.  Each vertex is a stance, each edge an allowed transition.

    The walker's state lives on *directed* edges: H_walker = C^{|E_directed|}.
    A coin operator (Grover diffusion across the edges of each vertex) mixes
    amplitudes leaving each vertex; the shift operator swaps the pair
    (u -> v) <-> (v -> u).  After t steps, the probability of being at vertex
    v is the sum of |amp(u -> v)|^2 over all u.

    This gives the quadratic (O(t)) diffusion signature that the plan requires
    while also handling irregular graphs (unlike the 1D line in the existing
    `quantum_walk_propagate`).
    """

    def __init__(self, adjacency: Dict[int, List[int]]) -> None:
        self.adjacency = {int(k): [int(v) for v in vs] for k, vs in adjacency.items()}
        self.vertices = sorted(self.adjacency.keys())
        # Directed-edge index: (src, dst) -> int
        self.edge_index: Dict[Tuple[int, int], int] = {}
        for u in self.vertices:
            for v in self.adjacency[u]:
                self.edge_index[(u, v)] = len(self.edge_index)
        self.n_edges = len(self.edge_index)

    # ------------------------------------------------------------------
    def _coin(self, amps: np.ndarray) -> np.ndarray:
        """Grover coin applied independently at every vertex."""
        out = np.zeros_like(amps)
        for u in self.vertices:
            neighbours = self.adjacency[u]
            if not neighbours:
                continue
            indices = [self.edge_index[(u, v)] for v in neighbours]
            local = amps[indices]
            avg = local.mean()
            # Grover: 2|s><s| - I
            out[indices] = 2.0 * avg - local
        return out

    def _shift(self, amps: np.ndarray) -> np.ndarray:
        """Flip (u -> v) amplitude with (v -> u)."""
        out = np.zeros_like(amps)
        for (u, v), idx in self.edge_index.items():
            if (v, u) in self.edge_index:
                out[self.edge_index[(v, u)]] = amps[idx]
        return out

    def step(self, amps: np.ndarray) -> np.ndarray:
        return self._shift(self._coin(amps))

    def initial_state(
        self,
        start_vertex: int,
        phases: Optional[Sequence[float]] = None,
    ) -> np.ndarray:
        """
        Superposition over outgoing edges of start_vertex.

        By default uses a *chirality-breaking* pattern: first outgoing edge
        weighted by (1+i)/sqrt(2), remaining edges by (1-i)/sqrt(2*(k-1)).
        This breaks the perfect symmetry that would otherwise trap the walker
        and reproduces the ballistic (~t) spread expected from a coined walk.
        Pass ``phases`` explicitly to override.
        """
        state = np.zeros(self.n_edges, dtype=complex)
        out_edges = [self.edge_index[(start_vertex, v)] for v in self.adjacency[start_vertex]]
        if not out_edges:
            raise ValueError(f"vertex {start_vertex} has no outgoing edges")
        k = len(out_edges)
        if phases is None:
            if k == 1:
                state[out_edges[0]] = 1.0
                return state
            # Chirality-breaking initial coin:
            #   weight first edge with amplitude  a = (1 + i) / sqrt(2)
            #   remaining edges with amplitude    b = (1 - i) / sqrt(2 (k-1))
            a = (1 + 1j) / np.sqrt(2.0)
            b = (1 - 1j) / np.sqrt(2.0 * (k - 1))
            state[out_edges[0]] = a / np.sqrt(2)
            for idx in out_edges[1:]:
                state[idx] = b / np.sqrt(2)
            # normalise
            state = state / np.linalg.norm(state)
            return state
        if len(phases) != k:
            raise ValueError("phases length must match outgoing degree")
        for idx, phi in zip(out_edges, phases):
            state[idx] = np.exp(1j * phi) / np.sqrt(k)
        return state

    def probabilities(self, amps: np.ndarray) -> Dict[int, float]:
        """Probability of occupying each vertex = sum |amp(*, v)|^2."""
        probs: Dict[int, float] = {v: 0.0 for v in self.vertices}
        for (u, v), idx in self.edge_index.items():
            probs[v] += float(np.abs(amps[idx]) ** 2)
        return probs

    def run(self, start_vertex: int, steps: int) -> List[Dict[int, float]]:
        state = self.initial_state(start_vertex)
        history = [self.probabilities(state)]
        for _ in range(steps):
            state = self.step(state)
            history.append(self.probabilities(state))
        return history


def classical_walk_on_graph(
    adjacency: Dict[int, List[int]],
    start_vertex: int,
    steps: int,
    seed: Optional[int] = None,
) -> List[Dict[int, float]]:
    """Reference classical random walk on the same graph (uniform transitions)."""
    vertices = sorted(adjacency.keys())
    probs = {v: 0.0 for v in vertices}
    probs[start_vertex] = 1.0
    history = [probs.copy()]
    for _ in range(steps):
        new = {v: 0.0 for v in vertices}
        for v in vertices:
            if probs[v] == 0 or not adjacency[v]:
                if not adjacency[v]:
                    new[v] += probs[v]  # absorb
                continue
            share = probs[v] / len(adjacency[v])
            for u in adjacency[v]:
                new[u] += share
        probs = new
        history.append(probs.copy())
    return history


def variance_on_cycle(
    n: int,
    steps: int,
    quantum: bool = True,
) -> float:
    """
    Second moment E[d^2] of the shortest-arc distance from the start vertex
    after `steps` steps on a cycle graph with n vertices.

    Because a coined quantum walk on a cycle spreads symmetrically, the mean
    signed displacement is zero and the classical-vs-quantum separation shows
    up in the *second moment* of the distance.  Classical walks give
    E[d^2] ~ t, quantum walks give E[d^2] ~ t^2 (ballistic spread).
    """
    adjacency = {i: [(i - 1) % n, (i + 1) % n] for i in range(n)}
    start = n // 2
    if quantum:
        history = GraphQuantumWalk(adjacency).run(start, steps)
    else:
        history = classical_walk_on_graph(adjacency, start, steps)
    probs = history[-1]
    total = sum(probs.values())
    if total <= 0:
        return 0.0
    m2 = 0.0
    for v, p in probs.items():
        dist = min(abs(v - start), n - abs(v - start))
        m2 += p * dist * dist / total
    return float(m2)
