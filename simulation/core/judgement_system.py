"""
Judgment System Module

This module defines various judge classes that evaluate moral actions,
introducing different types of biases, noise, and judgment strategies.
"""

import numpy as np
from typing import List, Optional, Callable
from abc import ABC, abstractmethod
from .action_space import Action


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

