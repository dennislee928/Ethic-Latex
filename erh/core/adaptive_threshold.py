"""
Adaptive Threshold Module

This module implements complexity-dependent adaptive thresholds for error assessment.

The key idea: as decision complexity increases, the uncertainty in moral evaluation
also increases, so we should be more tolerant of errors in complex cases.
"""

import numpy as np
from typing import List, Callable, Optional, Tuple
from scipy.optimize import minimize
from .action_space import Action


def linear_adaptive_threshold(complexity: int, tau_base: float = 0.3, slope: float = 0.1) -> float:
    """
    Linear adaptive threshold: τ(c) = τ₀ + slope * c
    
    Parameters
    ----------
    complexity : int
        Complexity value c
    tau_base : float, default=0.3
        Base threshold τ₀
    slope : float, default=0.1
        Rate of increase with complexity
        
    Returns
    -------
    float
        Adaptive threshold value
    """
    return tau_base + slope * complexity / 100.0


def logarithmic_adaptive_threshold(complexity: int, tau_base: float = 0.3, scale: float = 0.2) -> float:
    """
    Logarithmic adaptive threshold: τ(c) = τ₀ * (1 + scale * log(1 + c))
    
    Parameters
    ----------
    complexity : int
        Complexity value c
    tau_base : float, default=0.3
        Base threshold
    scale : float, default=0.2
        Scaling factor
        
    Returns
    -------
    float
        Adaptive threshold value
    """
    return tau_base * (1 + scale * np.log1p(complexity))


def power_adaptive_threshold(complexity: int, tau_base: float = 0.3, exponent: float = 0.3) -> float:
    """
    Power law adaptive threshold: τ(c) = τ₀ * (1 + c)^exponent
    
    Parameters
    ----------
    complexity : int
        Complexity value c
    tau_base : float, default=0.3
        Base threshold
    exponent : float, default=0.3
        Power exponent
        
    Returns
    -------
    float
        Adaptive threshold value
    """
    return tau_base * ((1 + complexity / 100.0) ** exponent)


def evaluate_judgment_with_adaptive_threshold(
    actions: List[Action],
    judge,
    threshold_function: Callable[[int], float],
    update_flags: bool = True
) -> None:
    """
    Evaluate judgments using an adaptive threshold function.
    
    Parameters
    ----------
    actions : List[Action]
        Actions to evaluate
    judge
        Judge instance with judge() method
    threshold_function : Callable
        Function mapping complexity → threshold
    update_flags : bool, default=True
        Whether to update mistake_flag based on adaptive threshold
    """
    for action in actions:
        # Get judgment
        J = judge.judge(action)
        action.J = J
        
        # Compute error
        delta = J - action.V
        action.delta = delta
        
        # Apply adaptive threshold
        tau_adaptive = threshold_function(action.c)
        error_magnitude = abs(delta)
        
        if update_flags:
            action.mistake_flag = 1 if error_magnitude > tau_adaptive else 0


def optimize_threshold_function(
    actions: List[Action],
    judge,
    function_type: str = 'linear',
    objective: str = 'minimize_weighted_errors'
) -> Tuple[Callable, dict]:
    """
    Optimize threshold function parameters to minimize objective.
    
    Parameters
    ----------
    actions : List[Action]
        Actions to use for optimization
    judge
        Judge instance
    function_type : {'linear', 'logarithmic', 'power'}, default='linear'
        Type of threshold function
    objective : {'minimize_weighted_errors', 'balance_fp_fn'}, default='minimize_weighted_errors'
        Optimization objective
        
    Returns
    -------
    threshold_function : Callable
        Optimized threshold function
    params : dict
        Optimized parameters
    """
    # Evaluate all actions first
    for action in actions:
        J = judge.judge(action)
        action.J = J
        action.delta = J - action.V
    
    def objective_linear(params):
        """Objective for linear threshold: τ(c) = p0 + p1*c"""
        tau_base, slope = params
        total_cost = 0.0
        
        for action in actions:
            tau = tau_base + slope * action.c / 100.0
            error_mag = abs(action.delta) if action.delta is not None else 0.0
            
            if objective == 'minimize_weighted_errors':
                # Cost = importance-weighted error if above threshold
                if error_mag > tau:
                    total_cost += action.w * error_mag
            elif objective == 'balance_fp_fn':
                # Balance false positives and false negatives
                is_mistake = error_mag > tau
                true_mistake = error_mag > 0.3  # Ground truth threshold
                
                if is_mistake and not true_mistake:  # False positive
                    total_cost += action.w * 0.5
                elif not is_mistake and true_mistake:  # False negative
                    total_cost += action.w * 1.0
        
        return total_cost
    
    def objective_logarithmic(params):
        """Objective for logarithmic threshold: τ(c) = p0 * (1 + p1*log(1+c))"""
        tau_base, scale = params
        total_cost = 0.0
        
        for action in actions:
            tau = tau_base * (1 + scale * np.log1p(action.c))
            error_mag = abs(action.delta) if action.delta is not None else 0.0
            
            if objective == 'minimize_weighted_errors':
                if error_mag > tau:
                    total_cost += action.w * error_mag
            elif objective == 'balance_fp_fn':
                is_mistake = error_mag > tau
                true_mistake = error_mag > 0.3
                
                if is_mistake and not true_mistake:
                    total_cost += action.w * 0.5
                elif not is_mistake and true_mistake:
                    total_cost += action.w * 1.0
        
        return total_cost
    
    def objective_power(params):
        """Objective for power threshold: τ(c) = p0 * (1 + c/100)^p1"""
        tau_base, exponent = params
        total_cost = 0.0
        
        for action in actions:
            tau = tau_base * ((1 + action.c / 100.0) ** exponent)
            error_mag = abs(action.delta) if action.delta is not None else 0.0
            
            if objective == 'minimize_weighted_errors':
                if error_mag > tau:
                    total_cost += action.w * error_mag
            elif objective == 'balance_fp_fn':
                is_mistake = error_mag > tau
                true_mistake = error_mag > 0.3
                
                if is_mistake and not true_mistake:
                    total_cost += action.w * 0.5
                elif not is_mistake and true_mistake:
                    total_cost += action.w * 1.0
        
        return total_cost
    
    # Select objective function
    if function_type == 'linear':
        obj_func = objective_linear
        initial_params = [0.3, 0.1]
        bounds = [(0.1, 0.5), (0.0, 0.5)]
    elif function_type == 'logarithmic':
        obj_func = objective_logarithmic
        initial_params = [0.3, 0.2]
        bounds = [(0.1, 0.5), (0.0, 1.0)]
    elif function_type == 'power':
        obj_func = objective_power
        initial_params = [0.3, 0.3]
        bounds = [(0.1, 0.5), (0.0, 1.0)]
    else:
        raise ValueError(f"Unknown function type: {function_type}")
    
    # Optimize
    result = minimize(obj_func, initial_params, method='Nelder-Mead', bounds=bounds, options={'maxiter': 50})
    
    if result.success:
        if function_type == 'linear':
            tau_base, slope = result.x
            threshold_function = lambda c: linear_adaptive_threshold(c, tau_base, slope)
            params = {'tau_base': tau_base, 'slope': slope, 'type': 'linear'}
        elif function_type == 'logarithmic':
            tau_base, scale = result.x
            threshold_function = lambda c: logarithmic_adaptive_threshold(c, tau_base, scale)
            params = {'tau_base': tau_base, 'scale': scale, 'type': 'logarithmic'}
        else:  # power
            tau_base, exponent = result.x
            threshold_function = lambda c: power_adaptive_threshold(c, tau_base, exponent)
            params = {'tau_base': tau_base, 'exponent': exponent, 'type': 'power'}
    else:
        # Fallback to default
        if function_type == 'linear':
            threshold_function = lambda c: linear_adaptive_threshold(c, 0.3, 0.1)
            params = {'tau_base': 0.3, 'slope': 0.1, 'type': 'linear'}
        elif function_type == 'logarithmic':
            threshold_function = lambda c: logarithmic_adaptive_threshold(c, 0.3, 0.2)
            params = {'tau_base': 0.3, 'scale': 0.2, 'type': 'logarithmic'}
        else:
            threshold_function = lambda c: power_adaptive_threshold(c, 0.3, 0.3)
            params = {'tau_base': 0.3, 'exponent': 0.3, 'type': 'power'}
    
    return threshold_function, params


def compare_fixed_vs_adaptive(
    actions: List[Action],
    judge,
    tau_fixed: float = 0.3,
    threshold_function: Optional[Callable] = None
) -> dict:
    """
    Compare fixed vs adaptive threshold approaches.
    
    Parameters
    ----------
    actions : List[Action]
        Actions to evaluate
    judge
        Judge instance
    tau_fixed : float, default=0.3
        Fixed threshold value
    threshold_function : Callable, optional
        Adaptive threshold function. If None, uses default linear.
        
    Returns
    -------
    dict
        Comparison metrics
    """
    # Fixed threshold evaluation
    actions_fixed = [Action(a.id, a.c, a.V, a.w) for a in actions]
    for action in actions_fixed:
        J = judge.judge(action)
        action.J = J
        action.delta = J - action.V
        action.mistake_flag = 1 if abs(action.delta) > tau_fixed else 0
    
    fixed_mistakes = sum(1 for a in actions_fixed if a.mistake_flag == 1)
    fixed_weighted = sum(a.w for a in actions_fixed if a.mistake_flag == 1)
    
    # Adaptive threshold evaluation
    if threshold_function is None:
        threshold_function = lambda c: linear_adaptive_threshold(c, tau_base=tau_fixed, slope=0.1)
    
    actions_adaptive = [Action(a.id, a.c, a.V, a.w) for a in actions]
    evaluate_judgment_with_adaptive_threshold(actions_adaptive, judge, threshold_function)
    
    adaptive_mistakes = sum(1 for a in actions_adaptive if a.mistake_flag == 1)
    adaptive_weighted = sum(a.w for a in actions_adaptive if a.mistake_flag == 1)
    
    # Complexity breakdown
    fixed_by_complexity = {}
    adaptive_by_complexity = {}
    
    for action_fixed, action_adaptive in zip(actions_fixed, actions_adaptive):
        c = action_fixed.c
        if c not in fixed_by_complexity:
            fixed_by_complexity[c] = {'total': 0, 'mistakes': 0}
            adaptive_by_complexity[c] = {'total': 0, 'mistakes': 0}
        
        fixed_by_complexity[c]['total'] += 1
        adaptive_by_complexity[c]['total'] += 1
        
        if action_fixed.mistake_flag == 1:
            fixed_by_complexity[c]['mistakes'] += 1
        if action_adaptive.mistake_flag == 1:
            adaptive_by_complexity[c]['mistakes'] += 1
    
    return {
        'fixed_mistakes': fixed_mistakes,
        'fixed_weighted': fixed_weighted,
        'adaptive_mistakes': adaptive_mistakes,
        'adaptive_weighted': adaptive_weighted,
        'difference': adaptive_mistakes - fixed_mistakes,
        'weighted_difference': adaptive_weighted - fixed_weighted,
        'fixed_by_complexity': fixed_by_complexity,
        'adaptive_by_complexity': adaptive_by_complexity
    }

