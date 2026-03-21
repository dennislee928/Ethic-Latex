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
