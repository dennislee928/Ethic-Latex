"""
Adversarial (Red Teaming) agent for ERH framework.

Optimizes inputs to maximize "Ethical Prime" discovery:
high importance, high failure rate - stress tests the judgment system.
"""

from typing import List, Callable, Optional
import numpy as np

from simulation.models import Action


class AdversarialAgent:
    """
    Red Teaming agent that seeks actions likely to become ethical primes.

    Maximizes: importance × failure_probability (high-stakes, high-error cases).
    """

    def __init__(
        self,
        judge_fn: Callable[[Action], float],
        tau: float = 0.3,
        max_iter: int = 100,
    ):
        """
        Parameters
        ----------
        judge_fn : callable
            Function that takes Action and returns judgment J
        tau : float
            Mistake threshold; |Δ| > τ → prime
        max_iter : int
            Max optimization iterations per candidate
        """
        self.judge_fn = judge_fn
        self.tau = tau
        self.max_iter = max_iter

    def _is_prime(self, action: Action) -> bool:
        J = self.judge_fn(action)
        delta = J - action.V
        return abs(delta) > self.tau

    def optimize_candidate(
        self,
        action: Action,
        perturb_scale: float = 0.2,
    ) -> Optional[Action]:
        """
        Perturb action (c, V, w) to increase prime likelihood.

        Tries small perturbations toward higher c (complexity) and w (importance).
        """
        best = action
        best_prime = self._is_prime(action)
        rng = np.random.default_rng(42)

        for _ in range(self.max_iter):
            c_new = int(np.clip(action.c + rng.integers(-5, 6), 1, 100))
            V_new = float(np.clip(action.V + rng.uniform(-perturb_scale, perturb_scale), -1, 1))
            w_new = float(max(0.1, action.w + rng.uniform(-0.2, 0.5)))

            cand = Action(id=action.id, c=c_new, V=V_new, w=w_new)
            if self._is_prime(cand):
                return cand
            if not best_prime and self._is_prime(cand):
                best = cand
                best_prime = True

        return best if best_prime else None

    def generate_adversarial_actions(
        self,
        base_actions: List[Action],
        target_count: int = 10,
    ) -> List[Action]:
        """
        From base_actions, find/generate actions that become primes.

        Returns up to target_count adversarial (prime) actions.
        """
        primes: List[Action] = []
        for a in base_actions:
            if len(primes) >= target_count:
                break
            adv = self.optimize_candidate(a)
            if adv is not None:
                primes.append(adv)
        return primes
