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
        method: str = 'annealing'
    ) -> Optional[Action]:
        """
        Perturb action (c, V, w) to maximize "primality" (failure probability).

        Tries to find small complexity perturbations that cause the judge to fail.
        """
        if method == 'random':
            # Basic random search fallback
            rng = np.random.default_rng(42)
            for _ in range(self.max_iter):
                c_new = int(np.clip(action.c + rng.integers(-5, 6), 1, 100))
                V_new = float(np.clip(action.V + rng.uniform(-perturb_scale, perturb_scale), -1, 1))
                w_new = float(max(0.1, action.w + rng.uniform(-0.2, 0.5)))
                cand = Action(id=action.id, c=c_new, V=V_new, w=w_new)
                if self._is_prime(cand): return cand
            return None

        # Simulated Annealing
        current = action
        T = 1.0
        decay = 0.95
        rng = np.random.default_rng(42)
        
        def get_score(a):
            # Score is distance from threshold (higher is better for attacker)
            J = self.judge_fn(a)
            delta = abs(J - a.V)
            # Bonus for high complexity and importance
            return delta + 0.1 * (a.c / 100.0) + 0.1 * (a.w / 10.0)

        best = current
        best_score = get_score(current)

        for _ in range(self.max_iter):
            # Perturb
            c_new = int(np.clip(current.c + rng.integers(-10, 11), 1, 100))
            V_new = float(np.clip(current.V + rng.uniform(-0.3, 0.3), -1, 1))
            w_new = float(np.clip(current.w + rng.uniform(-0.5, 0.5), 0.1, 10.0))
            
            cand = Action(id=current.id, c=c_new, V=V_new, w=w_new)
            cand_score = get_score(cand)
            
            if cand_score > best_score:
                best = cand
                best_score = cand_score
                current = cand
            elif np.exp((cand_score - best_score) / T) > rng.random():
                current = cand
            
            T *= decay
            if T < 0.01: break

        return best if self._is_prime(best) else None

    def attack_erh_bound(
        self,
        base_actions: List[Action],
        perturb_budget: float = 0.2
    ) -> List[Action]:
        """
        Attempt to break the ERH bound by inducing as many ethical primes as possible
        with minimal perturbations.
        """
        adversarial_actions = []
        for a in base_actions:
            adv = self.optimize_candidate(a, perturb_scale=perturb_budget)
            adversarial_actions.append(adv if adv else a)
        return adversarial_actions

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
