"""
Judgment System Module

This module defines various judge classes that evaluate moral actions,
introducing different types of biases, noise, and judgment strategies.

Supports optional QuantumOracle for non-binary superposition judgments.
GroundTruthProxy provides V(a) from human consensus / RLHF-style datasets.
"""

import csv
import json
import os
import numpy as np
from typing import List, Optional, Callable, Tuple, Dict, Any, Union, TYPE_CHECKING
from abc import ABC, abstractmethod
from pathlib import Path
from .action_space import Action

if TYPE_CHECKING:
    from simulation.quantum.interface import QuantumOracle


def _bradley_terry_v(
    preferences: List[Tuple[int, int, float]],
    action_ids: Optional[List[int]] = None,
    n_iter: int = 50,
) -> Dict[int, float]:
    """
    Bradley-Terry model: V(a) from pairwise preferences (winner_id, loser_id, margin).
    Returns action_id -> V in [-1, 1].
    """
    all_ids = set()
    for w, l, _ in preferences:
        all_ids.add(w)
        all_ids.add(l)
    ids = sorted(all_ids) if action_ids is None else list(action_ids)
    idx = {aid: i for i, aid in enumerate(ids)}
    n = len(ids)
    scores = np.zeros(n)
    for w, l, m in preferences:
        i, j = idx.get(w), idx.get(l)
        if i is not None:
            scores[i] += m
        if j is not None:
            scores[j] -= m
    scores = scores - scores.min()
    if scores.max() - scores.min() < 1e-12:
        return {aid: 0.0 for aid in ids}
    scaled = 2 * (scores - scores.min()) / (scores.max() - scores.min()) - 1
    return {aid: float(np.clip(scaled[idx[aid]], -1, 1)) for aid in ids}


class GroundTruthProxy:
    """
    Provides ground truth V(a) from human consensus or RLHF-weighted data.

    Replaces random "God view" with deterministic or dataset-driven values.
    Use mock data for simulation; load real RLHF/preference data for empirical studies.

    Parameters
    ----------
    data : Dict[int, float] or Dict[int, Tuple[float, float, float]]
        Maps action_id -> V, or action_id -> (V, ci_low, ci_high).
    default_ci_width : float, default=0.2
        Default half-width for confidence interval when not provided.
    """

    def __init__(
        self,
        data: Optional[Dict[int, Any]] = None,
        default_ci_width: float = 0.2,
    ):
        self._data = data or {}
        self.default_ci_width = default_ci_width

    def get_V(self, action: Action) -> float:
        """Return ground truth V(a). Falls back to action.V if missing."""
        val = self._data.get(action.id)
        if val is None:
            return action.V
        if isinstance(val, (list, tuple)) and len(val) >= 1:
            return float(val[0])
        return float(val)

    def get_confidence_interval(
        self,
        action: Action,
    ) -> Tuple[float, float]:
        """
        Return (ci_low, ci_high) for V(a).
        Uses stored interval if available; else centers on V with default width.
        """
        val = self._data.get(action.id)
        if val is not None and isinstance(val, (list, tuple)) and len(val) >= 3:
            return (float(val[1]), float(val[2]))
        v = self.get_V(action)
        w = self.default_ci_width
        return (np.clip(v - w, -1, 1), np.clip(v + w, -1, 1))

    @classmethod
    def from_mock_rlhf(
        cls,
        actions: List[Action],
        noise_scale: float = 0.1,
        n_annotators: int = 5,
        seed: Optional[int] = None,
    ) -> "GroundTruthProxy":
        """
        Build proxy from existing actions: V = action.V with annotator noise.
        Simulates RLHF-style human consensus with confidence intervals from
        annotator agreement variance.
        """
        if seed is not None:
            np.random.seed(seed)
        data = {}
        for a in actions:
            votes = [a.V + np.random.normal(0, noise_scale) for _ in range(n_annotators)]
            v = float(np.clip(np.mean(votes), -1, 1))
            std = float(np.std(votes))
            w = max(0.1, min(0.3, std + 0.05))
            data[a.id] = (v, np.clip(v - w, -1, 1), np.clip(v + w, -1, 1))
        return cls(data=data)

    @classmethod
    def load_from_csv(
        cls,
        path: Union[str, Path],
        id_col: str = "action_id",
        v_col: str = "V",
        ci_low_col: Optional[str] = "ci_low",
        ci_high_col: Optional[str] = "ci_high",
        confidence_col: Optional[str] = "confidence",
    ) -> "GroundTruthProxy":
        """
        Load ground truth from CSV with columns: action_id, V, and optionally
        ci_low, ci_high or confidence (for interval width).
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"CSV not found: {path}")
        data = {}
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                aid = int(row[id_col])
                v = float(row[v_col])
                if ci_low_col and ci_high_col and ci_low_col in row and ci_high_col in row:
                    data[aid] = (v, float(row[ci_low_col]), float(row[ci_high_col]))
                elif confidence_col and confidence_col in row:
                    w = float(row[confidence_col]) / 2
                    data[aid] = (v, np.clip(v - w, -1, 1), np.clip(v + w, -1, 1))
                else:
                    data[aid] = (v, np.clip(v - 0.2, -1, 1), np.clip(v + 0.2, -1, 1))
        return cls(data=data)

    @classmethod
    def load_from_json(
        cls,
        path: Union[str, Path],
        id_key: str = "action_id",
        v_key: str = "V",
    ) -> "GroundTruthProxy":
        """Load ground truth from JSON array of {action_id, V, ci_low?, ci_high?}."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"JSON not found: {path}")
        with open(path, encoding="utf-8") as f:
            arr = json.load(f)
        data = {}
        for obj in arr:
            aid = int(obj[id_key])
            v = float(obj[v_key])
            ci_low = obj.get("ci_low", v - 0.2)
            ci_high = obj.get("ci_high", v + 0.2)
            data[aid] = (v, float(np.clip(ci_low, -1, 1)), float(np.clip(ci_high, -1, 1)))
        return cls(data=data)

    @classmethod
    def from_rlhf_preferences(
        cls,
        preferences: List[Tuple[int, int, float]],
        action_ids: Optional[List[int]] = None,
    ) -> "GroundTruthProxy":
        """
        Build V(a) from RLHF pairwise preferences via Bradley-Terry.
        preferences: [(winner_id, loser_id, margin)].
        """
        v_map = _bradley_terry_v(preferences, action_ids)
        data = {aid: (v, np.clip(v - 0.15, -1, 1), np.clip(v + 0.15, -1, 1)) for aid, v in v_map.items()}
        return cls(data=data)


class BaseJudge(ABC):
    """
    Abstract base class for all judgment systems.
    
    A judge takes an action and produces a moral judgment J(a),
    which may differ from the true value V(a).
    """
    
    def __init__(self, name: str = "BaseJudge"):
        self.name = name
    
    @abstractmethod
    def judge(self, action: Action) -> float:
        """
        Produce a judgment for the given action.
        
        Parameters
        ----------
        action : Action
            The action to judge
            
        Returns
        -------
        float
            Judgment value J(a)
        """
        pass

    def judge_with_confidence(
        self,
        action: Action,
    ) -> Tuple[float, float, float]:
        """
        Produce judgment J(a) and a confidence interval (ci_low, ci_high).

        Default implementation uses judge() and estimates interval from
        judge-specific noise (e.g. noise_scale). Override for finer control.

        Returns
        -------
        tuple of (float, float, float)
            (J, ci_low, ci_high)
        """
        j = self.judge(action)
        width = getattr(self, "noise_scale", 0.2)
        ci_low = np.clip(j - width, -1, 1)
        ci_high = np.clip(j + width, -1, 1)
        return (float(j), float(ci_low), float(ci_high))
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"


class BiasedJudge(BaseJudge):
    """
    A judge with systematic bias that increases with complexity.
    
    This judge tends to systematically over- or under-estimate moral values,
    with the bias becoming stronger for more complex cases.
    
    Parameters
    ----------
    bias_strength : float, default=0.2
        Strength of the bias (positive = overestimate, negative = underestimate)
    noise_scale : float, default=0.1
        Standard deviation of random noise added to judgments
    complexity_dependency : float, default=0.5
        How much bias increases with complexity (0 = constant, 1 = linear)
    name : str, optional
        Name for this judge
        
    Examples
    --------
    >>> judge = BiasedJudge(bias_strength=0.3, noise_scale=0.1)
    >>> action = Action(id=0, c=50, V=0.5, w=1.0)
    >>> judgment = judge.judge(action)
    """
    
    def __init__(
        self,
        bias_strength: float = 0.2,
        noise_scale: float = 0.1,
        complexity_dependency: float = 0.5,
        name: str = "BiasedJudge"
    ):
        super().__init__(name)
        self.bias_strength = bias_strength
        self.noise_scale = noise_scale
        self.complexity_dependency = complexity_dependency
    
    def judge(self, action: Action) -> float:
        """
        Judge with complexity-dependent bias.
        
        J(a) = V(a) + bias * f(c) + noise
        where f(c) is a function of complexity
        """
        # Normalize complexity to [0, 1] (assuming max complexity ~100)
        c_normalized = action.c / 100.0
        
        # Bias increases with complexity
        bias_factor = 1 + self.complexity_dependency * c_normalized
        bias = self.bias_strength * bias_factor
        
        # Random noise
        noise = np.random.normal(0, self.noise_scale)
        
        # Compute judgment
        J = action.V + bias + noise
        
        # Clip to valid range
        return np.clip(J, -1, 1)


class NoisyJudge(BaseJudge):
    """
    A judge with high random noise but no systematic bias.
    
    This represents inconsistent judgment due to randomness,
    distraction, or lack of information.
    
    Parameters
    ----------
    noise_scale : float, default=0.3
        Standard deviation of the judgment noise
    complexity_scaling : bool, default=True
        If True, noise increases with complexity
    name : str, optional
        Name for this judge
    """
    
    def __init__(
        self,
        noise_scale: float = 0.3,
        complexity_scaling: bool = True,
        name: str = "NoisyJudge"
    ):
        super().__init__(name)
        self.noise_scale = noise_scale
        self.complexity_scaling = complexity_scaling
    
    def judge(self, action: Action) -> float:
        """
        Judge with complexity-dependent noise.
        """
        if self.complexity_scaling:
            # Noise increases with complexity
            c_normalized = action.c / 100.0
            effective_noise = self.noise_scale * (1 + c_normalized)
        else:
            effective_noise = self.noise_scale
        
        noise = np.random.normal(0, effective_noise)
        J = action.V + noise
        
        return np.clip(J, -1, 1)


class ConservativeJudge(BaseJudge):
    """
    A conservative judge that tends toward neutral (0) judgments.
    
    This represents risk-averse or cautious judgment that avoids extremes,
    especially for complex or uncertain cases.
    
    Parameters
    ----------
    threshold : float, default=0.5
        How strongly to pull toward neutral (0 = no effect, 1 = always neutral)
    noise_scale : float, default=0.1
        Random noise
    complexity_dependency : float, default=0.7
        How much conservatism increases with complexity
    name : str, optional
        Name for this judge
    """
    
    def __init__(
        self,
        threshold: float = 0.5,
        noise_scale: float = 0.1,
        complexity_dependency: float = 0.7,
        name: str = "ConservativeJudge"
    ):
        super().__init__(name)
        self.threshold = threshold
        self.noise_scale = noise_scale
        self.complexity_dependency = complexity_dependency
    
    def judge(self, action: Action) -> float:
        """
        Judge with tendency toward neutral values.
        """
        c_normalized = action.c / 100.0
        
        # Conservatism increases with complexity
        conservatism = self.threshold * (1 + self.complexity_dependency * c_normalized)
        conservatism = np.clip(conservatism, 0, 1)
        
        # Weighted average between true value and neutral (0)
        J = (1 - conservatism) * action.V + conservatism * 0
        
        # Add noise
        noise = np.random.normal(0, self.noise_scale)
        J += noise
        
        return np.clip(J, -1, 1)


class RadicalJudge(BaseJudge):
    """
    A radical judge that amplifies extremes and avoids neutral judgments.
    
    This represents polarized thinking that sees things in black and white.
    
    Parameters
    ----------
    amplification : float, default=1.5
        Factor by which to amplify judgments (>1)
    noise_scale : float, default=0.1
        Random noise
    name : str, optional
        Name for this judge
    """
    
    def __init__(
        self,
        amplification: float = 1.5,
        noise_scale: float = 0.1,
        name: str = "RadicalJudge"
    ):
        super().__init__(name)
        self.amplification = amplification
        self.noise_scale = noise_scale
    
    def judge(self, action: Action) -> float:
        """
        Judge with amplified values.
        """
        # Amplify the true value
        J = action.V * self.amplification
        
        # Add noise
        noise = np.random.normal(0, self.noise_scale)
        J += noise
        
        return np.clip(J, -1, 1)


class QuantumJudge(BaseJudge):
    """
    Judge that uses a QuantumOracle for superposition-based judgments.

    |ψ⟩ = α|Ethical⟩ + β|Unethical⟩; measurement yields J ∈ [-1, 1].
    """

    def __init__(
        self,
        quantum_oracle: "QuantumOracle",
        name: str = "QuantumJudge",
    ):
        super().__init__(name)
        self._oracle = quantum_oracle

    def judge(self, action: Action) -> float:
        difficulty = action.c / 100.0
        if hasattr(self._oracle, "judge_action"):
            return self._oracle.judge_action(difficulty)
        alpha_sq, beta_sq = self._oracle.collapse_wavefunction((difficulty,))
        return float(2 * alpha_sq - 1)


class CustomJudge(BaseJudge):
    """
    A judge with a custom judgment function.
    
    Parameters
    ----------
    judge_func : Callable[[Action], float]
        Custom function that takes an Action and returns a judgment
    name : str, optional
        Name for this judge
    """
    
    def __init__(
        self,
        judge_func: Callable[[Action], float],
        name: str = "CustomJudge"
    ):
        super().__init__(name)
        self.judge_func = judge_func
    
    def judge(self, action: Action) -> float:
        """
        Apply custom judgment function.
        """
        return self.judge_func(action)


def evaluate_action_quantum(
    action: Action,
    quantum_oracle: "QuantumOracle",
    tau: float = 0.3,
) -> float:
    """
    Evaluate a single action via quantum measurement.

    |ψ⟩ = α|Ethical⟩ + β|Unethical⟩; J = 2|α|² - 1 ∈ [-1, 1].

    Parameters
    ----------
    action : Action
        Action to judge
    quantum_oracle : QuantumOracle
        Oracle with judge_action(difficulty) method
    tau : float
        Mistake threshold (for consistency; not used in quantum path)

    Returns
    -------
    float
        Judgment J(a)
    """
    difficulty = action.c / 100.0
    if hasattr(quantum_oracle, "judge_action"):
        return quantum_oracle.judge_action(difficulty)
    alpha_sq, _ = quantum_oracle.collapse_wavefunction((difficulty,))
    return float(2 * alpha_sq - 1)


def evaluate_judgement(
    actions: List[Action],
    judge: BaseJudge,
    tau: float = 0.3,
    inplace: bool = True
) -> Optional[List[Action]]:
    """
    Evaluate all actions with a given judge and compute errors.
    
    For each action, this function:
    1. Computes judgment J(a) using the judge
    2. Computes error Δ(a) = J(a) - V(a)
    3. Sets mistake_flag to 1 if |Δ(a)| > τ, else 0
    
    Parameters
    ----------
    actions : List[Action]
        List of actions to evaluate
    judge : BaseJudge
        The judge to use for evaluation
    tau : float, default=0.3
        Threshold for considering a judgment a "mistake"
        If |Δ(a)| > τ, then mistake_flag = 1
    inplace : bool, default=True
        If True, modify actions in place. If False, return a copy.
        
    Returns
    -------
    Optional[List[Action]]
        If inplace=False, returns a new list of actions with judgments.
        If inplace=True, returns None and modifies input list.
        
    Examples
    --------
    >>> actions = generate_world(100)
    >>> judge = BiasedJudge(bias_strength=0.2)
    >>> evaluate_judgement(actions, judge, tau=0.3)
    >>> mistakes = sum(a.mistake_flag for a in actions)
    >>> print(f"Total mistakes: {mistakes}")
    """
    if not inplace:
        import copy
        actions = copy.deepcopy(actions)
    
    for action in actions:
        # Get judgment
        action.J = judge.judge(action)
        
        # Compute error
        action.delta = action.J - action.V
        
        # Set mistake flag
        action.mistake_flag = 1 if abs(action.delta) > tau else 0
    
    if not inplace:
        return actions


def batch_evaluate(
    actions: List[Action],
    judges: dict,
    tau: float = 0.3
) -> dict:
    """
    Evaluate actions with multiple judges.
    
    Parameters
    ----------
    actions : List[Action]
        List of actions to evaluate
    judges : dict
        Dictionary mapping judge names to BaseJudge instances
    tau : float, default=0.3
        Mistake threshold
        
    Returns
    -------
    dict
        Dictionary mapping judge names to lists of evaluated actions
        Each action list is an independent copy.
        
    Examples
    --------
    >>> actions = generate_world(100)
    >>> judges = {
    ...     'biased': BiasedJudge(bias_strength=0.2),
    ...     'noisy': NoisyJudge(noise_scale=0.3),
    ...     'conservative': ConservativeJudge()
    ... }
    >>> results = batch_evaluate(actions, judges)
    >>> for name, evaluated_actions in results.items():
    ...     mistakes = sum(a.mistake_flag for a in evaluated_actions)
    ...     print(f"{name}: {mistakes} mistakes")
    """
    import copy
    results = {}
    
    for name, judge in judges.items():
        # Create a deep copy for each judge
        actions_copy = copy.deepcopy(actions)
        evaluate_judgement(actions_copy, judge, tau=tau, inplace=True)
        results[name] = actions_copy
    
    return results


def compute_judgment_metrics(actions: List[Action]) -> dict:
    """
    Compute various metrics about judgment quality.
    
    Parameters
    ----------
    actions : List[Action]
        List of actions with judgments
        
    Returns
    -------
    dict
        Dictionary of metrics including MAE, RMSE, mistake rate, etc.
    """
    deltas = [a.delta for a in actions if a.delta is not None]
    mistakes = [a.mistake_flag for a in actions if a.mistake_flag is not None]
    
    if not deltas:
        return {}
    
    metrics = {
        'mae': np.mean(np.abs(deltas)),
        'rmse': np.sqrt(np.mean(np.array(deltas)**2)),
        'mean_error': np.mean(deltas),
        'std_error': np.std(deltas),
        'max_error': np.max(np.abs(deltas)),
        'mistake_count': sum(mistakes),
        'mistake_rate': np.mean(mistakes),
        'total_actions': len(actions)
    }
    
    return metrics


# ---------------------------------------------------------------------------
# Re-export new judge classes and data types from erh_core
# ---------------------------------------------------------------------------
try:
    from erh_core.core.judgement_system import (
        DecisionTrace,
        IntersectionalJudge,
        TemporalJudge,
        CounterfactualJudge,
        FederatedJudge,
    )
except ImportError:
    pass  # erh_core not installed; new classes unavailable in this environment
