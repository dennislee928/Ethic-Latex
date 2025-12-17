"""
Probabilistic Moral Values Module

This module represents true moral values as probability distributions
rather than fixed values, modeling uncertainty and disagreement.
"""

import numpy as np
from typing import List, Optional, Tuple
from scipy.stats import norm, beta
from .action_space import Action


def generate_probabilistic_action(
    action_id: int,
    complexity: int,
    importance: float,
    value_distribution: str = 'gaussian',
    mu: Optional[float] = None,
    sigma: Optional[float] = None,
    alpha: Optional[float] = None,
    beta_param: Optional[float] = None
) -> Action:
    """
    Generate an action with probabilistic true moral value.
    
    Parameters
    ----------
    action_id : int
        Action identifier
    complexity : int
        Complexity level
    importance : float
        Importance weight
    value_distribution : {'gaussian', 'beta'}, default='gaussian'
        Type of distribution for true value
    mu : float, optional
        Mean for Gaussian distribution
    sigma : float, optional
        Standard deviation for Gaussian
    alpha : float, optional
        Alpha parameter for Beta distribution
    beta_param : float, optional
        Beta parameter for Beta distribution
        
    Returns
    -------
    Action
        Action with probabilistic true value (V is the mean)
    """
    if value_distribution == 'gaussian':
        if mu is None:
            mu = np.random.uniform(-0.5, 0.5)
        if sigma is None:
            sigma = 0.2
        
        # Store distribution parameters as attributes
        action = Action(id=action_id, c=complexity, V=mu, w=importance)
        action.value_distribution = 'gaussian'
        action.value_mu = mu
        action.value_sigma = sigma
        return action
    
    elif value_distribution == 'beta':
        # Beta distribution scaled to [-1, 1]
        if alpha is None:
            alpha = 2.0
        if beta_param is None:
            beta_param = 2.0
        
        # Sample from Beta(0,1) then scale to [-1, 1]
        beta_sample = beta.rvs(alpha, beta_param)
        mu = 2 * beta_sample - 1  # Scale to [-1, 1]
        
        action = Action(id=action_id, c=complexity, V=mu, w=importance)
        action.value_distribution = 'beta'
        action.value_alpha = alpha
        action.value_beta = beta_param
        return action
    
    else:
        raise ValueError(f"Unknown distribution: {value_distribution}")


def compute_expected_error(
    action: Action,
    judgment: float
) -> float:
    """
    Compute expected error for probabilistic true value.
    
    E[|J - V|] where V ~ distribution
    
    Parameters
    ----------
    action : Action
        Action with probabilistic true value
    judgment : float
        Judgment value J(a)
        
    Returns
    -------
    float
        Expected absolute error
    """
    if not hasattr(action, 'value_distribution'):
        # Fallback to deterministic
        return abs(judgment - action.V)
    
    if action.value_distribution == 'gaussian':
        mu = getattr(action, 'value_mu', action.V)
        sigma = getattr(action, 'value_sigma', 0.2)
        
        # E[|J - V|] for V ~ N(mu, sigma^2)
        # Approximation: |J - mu| + sigma * sqrt(2/pi)
        expected_error = abs(judgment - mu) + sigma * np.sqrt(2 / np.pi)
        return expected_error
    
    elif action.value_distribution == 'beta':
        # For Beta, use mean as approximation
        mu = action.V
        # Rough approximation
        alpha = getattr(action, 'value_alpha', 2.0)
        beta_param = getattr(action, 'value_beta', 2.0)
        variance = (alpha * beta_param) / ((alpha + beta_param) ** 2 * (alpha + beta_param + 1))
        sigma = np.sqrt(variance) * 2  # Scaled to [-1, 1] range
        
        expected_error = abs(judgment - mu) + sigma * np.sqrt(2 / np.pi)
        return expected_error
    
    else:
        return abs(judgment - action.V)


def compute_error_variance(
    action: Action,
    judgment: float
) -> float:
    """
    Compute variance of error for probabilistic true value.
    
    Var[|J - V|]
    
    Parameters
    ----------
    action : Action
        Action with probabilistic true value
    judgment : float
        Judgment value
        
    Returns
    -------
    float
        Error variance
    """
    if not hasattr(action, 'value_distribution'):
        return 0.0
    
    if action.value_distribution == 'gaussian':
        sigma = getattr(action, 'value_sigma', 0.2)
        # Approximation for variance of |J - V|
        return sigma ** 2
    
    else:
        return 0.1  # Default small variance


def evaluate_with_uncertainty(
    actions: List[Action],
    judge,
    tau: float = 0.3,
    use_expected_error: bool = True
) -> None:
    """
    Evaluate actions accounting for probabilistic true values.
    
    Parameters
    ----------
    actions : List[Action]
        Actions to evaluate
    judge
        Judge instance
    tau : float, default=0.3
        Error threshold
    use_expected_error : bool, default=True
        If True, use expected error. If False, sample from distribution.
    """
    for action in actions:
        J = judge.judge(action)
        action.J = J
        
        if use_expected_error:
            # Use expected error
            expected_err = compute_expected_error(action, J)
            action.delta = J - action.V  # Store deterministic delta
            action.expected_error = expected_err
            action.mistake_flag = 1 if expected_err > tau else 0
        else:
            # Sample true value from distribution
            if hasattr(action, 'value_distribution'):
                if action.value_distribution == 'gaussian':
                    mu = getattr(action, 'value_mu', action.V)
                    sigma = getattr(action, 'value_sigma', 0.2)
                    V_sampled = np.clip(norm.rvs(mu, sigma), -1, 1)
                else:
                    V_sampled = action.V
            else:
                V_sampled = action.V
            
            delta = J - V_sampled
            action.delta = delta
            action.mistake_flag = 1 if abs(delta) > tau else 0


def model_subjective_disagreement(
    actions: List[Action],
    num_evaluators: int = 5,
    evaluator_bias_range: Tuple[float, float] = (-0.3, 0.3)
) -> Dict:
    """
    Model multiple evaluators with different perspectives on true values.
    
    Parameters
    ----------
    actions : List[Action]
        Actions to evaluate
    num_evaluators : int, default=5
        Number of evaluators
    evaluator_bias_range : Tuple[float, float], default=(-0.3, 0.3)
        Range of biases for different evaluators
        
    Returns
    -------
    dict
        Results including consensus scores and disagreement measures
    """
    evaluator_values = {}
    
    for evaluator_id in range(num_evaluators):
        bias = np.random.uniform(*evaluator_bias_range)
        values = []
        
        for action in actions:
            # Each evaluator has slightly different true value
            V_evaluator = np.clip(action.V + bias + np.random.normal(0, 0.1), -1, 1)
            values.append(V_evaluator)
        
        evaluator_values[evaluator_id] = values
    
    # Compute consensus and disagreement
    consensus_scores = []
    disagreement_scores = []
    
    for i, action in enumerate(actions):
        values = [evaluator_values[eid][i] for eid in range(num_evaluators)]
        mean_value = np.mean(values)
        std_value = np.std(values)
        
        consensus_scores.append(1.0 / (1.0 + std_value))  # Higher std = lower consensus
        disagreement_scores.append(std_value)
    
    return {
        'evaluator_values': evaluator_values,
        'consensus_scores': consensus_scores,
        'disagreement_scores': disagreement_scores,
        'mean_consensus': np.mean(consensus_scores),
        'mean_disagreement': np.mean(disagreement_scores),
        'actions_with_high_disagreement': [
            i for i, d in enumerate(disagreement_scores) if d > np.percentile(disagreement_scores, 75)
        ]
    }

