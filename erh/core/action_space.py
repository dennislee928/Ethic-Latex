"""
Action Space Module

This module defines the Action class and functions for generating moral action spaces
with various complexity and value distributions.
"""

import numpy as np
from typing import List, Optional, Literal
from dataclasses import dataclass


@dataclass
class Action:
    """
    Represents a single action/case in the moral judgment space.
    
    Attributes
    ----------
    id : int
        Unique identifier for the action
    c : int
        Complexity level (positive integer)
    V : float
        True moral value (ground truth), typically in [-1, 1]
        -1 = extremely immoral, 0 = neutral, +1 = extremely moral
    w : float
        Importance weight (e.g., number of people affected, severity)
    J : Optional[float]
        Judgment value assigned by a judge (initially None)
    delta : Optional[float]
        Error: Δ(a) = J(a) - V(a) (initially None)
    mistake_flag : Optional[int]
        Binary indicator: 1 if |Δ| > τ, 0 otherwise (initially None)
    """
    id: int
    c: int  # complexity
    V: float  # true moral value
    w: float  # importance weight
    J: Optional[float] = None  # judgment
    delta: Optional[float] = None  # error
    mistake_flag: Optional[int] = None  # misjudgment indicator
    severity: Optional[float] = None  # fuzzy severity (0-1) for continuous error assessment
    
    def __repr__(self):
        return f"Action(id={self.id}, c={self.c}, V={self.V:.2f}, w={self.w:.2f})"


def generate_world(
    num_actions: int = 1000,
    complexity_dist: Literal['uniform', 'zipf', 'power_law'] = 'zipf',
    complexity_range: tuple = (1, 100),
    moral_ambiguity_factor: float = 0.3,
    importance_correlation: float = 0.5,
    random_seed: Optional[int] = None
) -> List[Action]:
    """
    Generate a moral action space with specified distributions.
    
    Parameters
    ----------
    num_actions : int, default=1000
        Number of actions to generate
    complexity_dist : {'uniform', 'zipf', 'power_law'}, default='zipf'
        Distribution type for complexity values
        - 'uniform': Uniform distribution
        - 'zipf': Zipf distribution (realistic for real-world cases)
        - 'power_law': Power law distribution
    complexity_range : tuple, default=(1, 100)
        (min_complexity, max_complexity)
    moral_ambiguity_factor : float, default=0.3
        Controls how complexity affects moral clarity
        Higher values = more ambiguity for complex cases
        0 = no effect, 1 = maximum effect
    importance_correlation : float, default=0.5
        Correlation between complexity and importance
        0 = no correlation, 1 = perfect correlation
    random_seed : Optional[int], default=None
        Random seed for reproducibility
        
    Returns
    -------
    List[Action]
        List of Action objects with initialized c, V, w values
        
    Examples
    --------
    >>> actions = generate_world(num_actions=500, complexity_dist='zipf')
    >>> print(f"Generated {len(actions)} actions")
    >>> print(f"Complexity range: {min(a.c for a in actions)} to {max(a.c for a in actions)}")
    
    Notes
    -----
    The moral value V(a) is generated such that:
    - Low complexity cases tend to have clear values (closer to -1 or +1)
    - High complexity cases tend to be more ambiguous (closer to 0)
    
    This reflects the intuition that simple moral cases are often clear-cut,
    while complex cases involve multiple considerations and trade-offs.
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    min_c, max_c = complexity_range
    actions = []
    
    # Generate complexity values
    if complexity_dist == 'uniform':
        complexities = np.random.randint(min_c, max_c + 1, size=num_actions)
    elif complexity_dist == 'zipf':
        # Zipf distribution: many simple cases, few complex ones
        # a parameter controls the distribution shape
        zipf_samples = np.random.zipf(a=2.0, size=num_actions)
        complexities = np.clip(zipf_samples, min_c, max_c)
    elif complexity_dist == 'power_law':
        # Power law with exponent
        uniform = np.random.uniform(0, 1, size=num_actions)
        complexities = min_c + (max_c - min_c) * (uniform ** 2)
        complexities = complexities.astype(int)
    else:
        raise ValueError(f"Unknown complexity_dist: {complexity_dist}")
    
    for i in range(num_actions):
        c = int(complexities[i])
        
        # Generate true moral value with complexity-dependent ambiguity
        # Ambiguity increases with complexity
        ambiguity = moral_ambiguity_factor * (c - min_c) / (max_c - min_c)
        
        # Base moral value: random with tendency toward extremes for simple cases
        if np.random.random() < ambiguity:
            # Ambiguous case: closer to 0
            V = np.random.normal(0, 0.3)
        else:
            # Clear case: closer to -1 or +1
            sign = np.random.choice([-1, 1])
            magnitude = np.random.beta(2, 1)  # skewed toward 1
            V = sign * magnitude
        
        # Clip to [-1, 1]
        V = np.clip(V, -1, 1)
        
        # Generate importance weight
        # Partially correlated with complexity
        base_importance = np.random.gamma(shape=2, scale=1)
        complexity_factor = importance_correlation * (c / max_c)
        w = base_importance * (1 + complexity_factor)
        
        action = Action(
            id=i,
            c=c,
            V=V,
            w=w
        )
        actions.append(action)
    
    return actions


def sample_complexity(
    distribution: str = 'zipf',
    min_val: int = 1,
    max_val: int = 100,
    **kwargs
) -> int:
    """
    Sample a single complexity value from a specified distribution.
    
    Parameters
    ----------
    distribution : str, default='zipf'
        Distribution type
    min_val : int, default=1
        Minimum complexity
    max_val : int, default=100
        Maximum complexity
    **kwargs
        Additional parameters for the distribution
        
    Returns
    -------
    int
        Sampled complexity value
    """
    if distribution == 'uniform':
        return np.random.randint(min_val, max_val + 1)
    elif distribution == 'zipf':
        a = kwargs.get('a', 2.0)
        sample = np.random.zipf(a)
        return int(np.clip(sample, min_val, max_val))
    else:
        return np.random.randint(min_val, max_val + 1)


def get_action_statistics(actions: List[Action]) -> dict:
    """
    Compute summary statistics for a list of actions.
    
    Parameters
    ----------
    actions : List[Action]
        List of actions to analyze
        
    Returns
    -------
    dict
        Dictionary containing various statistics
    """
    complexities = [a.c for a in actions]
    values = [a.V for a in actions]
    weights = [a.w for a in actions]
    
    stats = {
        'num_actions': len(actions),
        'complexity': {
            'min': np.min(complexities),
            'max': np.max(complexities),
            'mean': np.mean(complexities),
            'median': np.median(complexities),
            'std': np.std(complexities)
        },
        'moral_value': {
            'min': np.min(values),
            'max': np.max(values),
            'mean': np.mean(values),
            'median': np.median(values),
            'std': np.std(values),
            'positive_ratio': sum(1 for v in values if v > 0) / len(values),
            'negative_ratio': sum(1 for v in values if v < 0) / len(values),
            'neutral_ratio': sum(1 for v in values if abs(v) < 0.1) / len(values)
        },
        'importance': {
            'min': np.min(weights),
            'max': np.max(weights),
            'mean': np.mean(weights),
            'median': np.median(weights),
            'std': np.std(weights)
        }
    }
    
    # Add judgment statistics if available
    if actions[0].J is not None:
        judgments = [a.J for a in actions]
        deltas = [a.delta for a in actions if a.delta is not None]
        mistakes = [a.mistake_flag for a in actions if a.mistake_flag is not None]
        
        stats['judgment'] = {
            'mean': np.mean(judgments),
            'std': np.std(judgments)
        }
        stats['error'] = {
            'mean': np.mean(deltas),
            'std': np.std(deltas),
            'mae': np.mean(np.abs(deltas)),
            'rmse': np.sqrt(np.mean(np.array(deltas)**2))
        }
        stats['mistakes'] = {
            'count': sum(mistakes),
            'rate': np.mean(mistakes)
        }
    
    return stats

