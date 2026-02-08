"""
Action Space Module

This module defines the Action class and functions for generating moral action spaces
with various complexity and value distributions.

Action is a Pydantic model for type safety and runtime validation (see simulation.models).
"""

import numpy as np
from typing import List, Optional, Literal

import math
from simulation.models import Action, ETHICAL_PRINCIPLES


def count_principle_conflicts(action: Action) -> int:
    """
    Count the number of conflicting ethical principles for an action.

    Uses principle_conflict_pairs if set; else infers from active_principles
    via a default conflict matrix (Deontology vs Utilitarianism, etc.).
    Returns 0 if neither is set.

    Parameters
    ----------
    action : Action
        Action with optional active_principles and principle_conflict_pairs.

    Returns
    -------
    int
        Number of conflicting principle pairs.
    """
    pairs = getattr(action, "principle_conflict_pairs", None)
    if pairs is not None and len(pairs) > 0:
        return len(pairs)

    active = getattr(action, "active_principles", None)
    if active is None or len(active) < 2:
        return 0

    # Default conflict matrix: canonical conflicts (e.g. Deontology vs Utilitarianism)
    # (0,1), (0,2), (1,2) etc. - indices into ETHICAL_PRINCIPLES
    n = len(ETHICAL_PRINCIPLES)
    conflict_count = 0
    for i, pi in enumerate(active):
        for pj in active[i + 1:]:
            if pi != pj and 0 <= pi < n and 0 <= pj < n:
                conflict_count += 1
    return conflict_count


def calculate_complexity(
    action: Action,
    use_token_proxy: bool = False,
    use_principle_conflicts: bool = True,
) -> int:
    """
    Compute concrete complexity c(a) for an action.

    Primary metric: Number of conflicting ethical principles
    (e.g., Deontology vs. Utilitarianism count). Uses principle_conflict_pairs
    or active_principles when available; else conflicting_principles or c.

    Token-length proxy: When action has a description and use_token_proxy=True,
    uses log(1 + word_count) as a proxy for reasoning complexity.
    Combined with principle count when both are available.

    Parameters
    ----------
    action : Action
        The action to evaluate.
    use_token_proxy : bool, default=False
        If True and action has description, incorporate token-length proxy.
    use_principle_conflicts : bool, default=True
        If True, prefer counting from principle_conflict_pairs/active_principles.

    Returns
    -------
    int
        Complexity value (≥ 0).

    Examples
    --------
    >>> a = Action(id=0, c=5, V=0.3, w=1.0, conflicting_principles=3)
    >>> calculate_complexity(a)
    3
    >>> a2 = Action(id=1, c=10, V=0.5, w=1.0, active_principles=[0,1,2],
    ...            principle_conflict_pairs=[(0,1),(1,2)])
    >>> calculate_complexity(a2)  # 2 explicit conflicts
    2
    """
    c_principle = action.c

    if use_principle_conflicts:
        conflict_count = count_principle_conflicts(action)
        if conflict_count > 0:
            c_principle = conflict_count
        else:
            base = getattr(action, "conflicting_principles", None)
            if base is not None:
                c_principle = int(base)

    if use_token_proxy and hasattr(action, "description") and action.description:
        word_count = len(str(action.description).split())
        token_proxy = int(math.log(1 + word_count) * 10)
        c_principle = max(c_principle, token_proxy)

    return max(0, c_principle)


def generate_world(
    num_actions: int = 1000,
    complexity_dist: Literal['uniform', 'zipf', 'power_law'] = 'zipf',
    complexity_range: tuple = (1, 100),
    moral_ambiguity_factor: float = 0.3,
    importance_correlation: float = 0.5,
    random_seed: Optional[int] = None,
    set_conflicting_principles: bool = False,
    set_principle_conflicts: bool = False,
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

        kwargs = {"id": i, "c": c, "V": float(V), "w": float(w)}
        if set_conflicting_principles:
            kwargs["conflicting_principles"] = c
        if set_principle_conflicts:
            n_principles = len(ETHICAL_PRINCIPLES)
            k = min(max(2, c), n_principles)
            active = np.random.choice(n_principles, size=k, replace=False).tolist()
            pairs = [(active[xi], active[yi]) for xi in range(len(active)) for yi in range(xi + 1, len(active))]
            kwargs["active_principles"] = active
            kwargs["principle_conflict_pairs"] = pairs[: max(1, min(len(pairs), c))]
        action = Action(**kwargs)
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

