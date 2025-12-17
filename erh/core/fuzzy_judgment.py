"""
Fuzzy Judgment Module

This module implements fuzzy logic for error assessment, replacing binary
mistake flags with continuous severity measures.

Instead of a hard threshold τ, errors are assessed with continuous severity
functions that smoothly transition near the threshold.
"""

import numpy as np
from typing import List, Literal, Optional, Callable
from .action_space import Action


def triangular_membership(x: float, a: float, b: float, c: float) -> float:
    """
    Triangular fuzzy membership function.
    
    Parameters
    ----------
    x : float
        Input value
    a : float
        Left vertex (membership = 0)
    b : float
        Peak vertex (membership = 1)
    c : float
        Right vertex (membership = 0)
        
    Returns
    -------
    float
        Membership value in [0, 1]
    """
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a) if b > a else 0.0
    else:  # b < x < c
        return (c - x) / (c - b) if c > b else 0.0


def trapezoidal_membership(x: float, a: float, b: float, c: float, d: float) -> float:
    """
    Trapezoidal fuzzy membership function.
    
    Parameters
    ----------
    x : float
        Input value
    a : float
        Left bottom (membership = 0)
    b : float
        Left top (membership = 1)
    c : float
        Right top (membership = 1)
    d : float
        Right bottom (membership = 0)
        
    Returns
    -------
    float
        Membership value in [0, 1]
    """
    if x <= a or x >= d:
        return 0.0
    elif a < x < b:
        return (x - a) / (b - a) if b > a else 0.0
    elif b <= x <= c:
        return 1.0
    else:  # c < x < d
        return (d - x) / (d - c) if d > c else 0.0


def gaussian_membership(x: float, center: float, width: float) -> float:
    """
    Gaussian fuzzy membership function.
    
    Parameters
    ----------
    x : float
        Input value
    center : float
        Center of the membership function
    width : float
        Width parameter (standard deviation)
        
    Returns
    -------
    float
        Membership value in [0, 1]
    """
    if width <= 0:
        return 1.0 if abs(x - center) < 1e-10 else 0.0
    return np.exp(-0.5 * ((x - center) / width) ** 2)


def compute_fuzzy_severity(
    error_magnitude: float,
    tau: float,
    membership_type: Literal['triangular', 'trapezoidal', 'gaussian'] = 'triangular',
    smoothness: float = 0.2
) -> float:
    """
    Compute fuzzy severity of an error.
    
    Severity is a continuous measure in [0, 1] indicating how "serious" the error is.
    
    Parameters
    ----------
    error_magnitude : float
        |Δ(a)| - absolute error magnitude
    tau : float
        Threshold parameter
    membership_type : {'triangular', 'trapezoidal', 'gaussian'}, default='triangular'
        Type of membership function
    smoothness : float, default=0.2
        Controls transition smoothness (fraction of tau)
        
    Returns
    -------
    float
        Severity in [0, 1]
    """
    if membership_type == 'triangular':
        # Triangular: 0 at tau-smoothness, 1 at tau+smoothness
        a = max(0, tau * (1 - smoothness))
        b = tau
        c = tau * (1 + smoothness)
        return triangular_membership(error_magnitude, a, b, c)
    
    elif membership_type == 'trapezoidal':
        # Trapezoidal: smooth transition zone
        a = max(0, tau * (1 - smoothness))
        b = tau * (1 - smoothness * 0.5)
        c = tau * (1 + smoothness * 0.5)
        d = tau * (1 + smoothness)
        return trapezoidal_membership(error_magnitude, a, b, c, d)
    
    elif membership_type == 'gaussian':
        # Gaussian: centered at tau
        center = tau
        width = tau * smoothness
        # For errors above tau, use increasing function
        if error_magnitude < tau:
            return gaussian_membership(error_magnitude, center, width)
        else:
            # Above threshold: severity increases
            base_severity = gaussian_membership(tau, center, width)
            excess = error_magnitude - tau
            additional = min(1.0 - base_severity, excess / (tau * smoothness))
            return base_severity + additional
    
    else:
        raise ValueError(f"Unknown membership type: {membership_type}")


def compute_adaptive_severity(
    error_magnitude: float,
    complexity: int,
    tau_base: float = 0.3,
    complexity_factor: float = 0.1
) -> float:
    """
    Compute adaptive severity where threshold depends on complexity.
    
    Higher complexity → higher tolerance → lower severity for same error.
    
    Parameters
    ----------
    error_magnitude : float
        |Δ(a)|
    complexity : int
        Complexity c(a)
    tau_base : float, default=0.3
        Base threshold
    complexity_factor : float, default=0.1
        How much threshold increases with complexity
        
    Returns
    -------
    float
        Adaptive severity in [0, 1]
    """
    # Adaptive threshold: τ(c) = τ₀ * (1 + factor * c)
    tau_adaptive = tau_base * (1 + complexity_factor * complexity / 100.0)
    
    # Use triangular membership with adaptive threshold
    return compute_fuzzy_severity(
        error_magnitude, 
        tau_adaptive, 
        membership_type='triangular',
        smoothness=0.2
    )


def assign_fuzzy_severities(
    actions: List[Action],
    tau: float = 0.3,
    membership_type: Literal['triangular', 'trapezoidal', 'gaussian'] = 'triangular',
    adaptive: bool = False,
    smoothness: float = 0.2
) -> None:
    """
    Assign fuzzy severity scores to actions based on their errors.
    
    This replaces or supplements the binary mistake_flag with a continuous
    severity measure stored in action.severity.
    
    Parameters
    ----------
    actions : List[Action]
        List of actions to evaluate
    tau : float, default=0.3
        Error threshold
    membership_type : {'triangular', 'trapezoidal', 'gaussian'}, default='triangular'
        Type of membership function
    adaptive : bool, default=False
        If True, use complexity-adaptive thresholds
    smoothness : float, default=0.2
        Transition smoothness parameter
    """
    for action in actions:
        if action.delta is None:
            action.severity = 0.0
            continue
        
        error_magnitude = abs(action.delta)
        
        if adaptive:
            severity = compute_adaptive_severity(
                error_magnitude, 
                action.c, 
                tau_base=tau,
                complexity_factor=0.1
            )
        else:
            severity = compute_fuzzy_severity(
                error_magnitude,
                tau,
                membership_type=membership_type,
                smoothness=smoothness
            )
        
        # Store severity (add as attribute if not exists)
        action.severity = severity
        
        # Also update mistake_flag based on severity (threshold at 0.5)
        if not hasattr(action, 'mistake_flag') or action.mistake_flag is None:
            action.mistake_flag = 1 if severity > 0.5 else 0


def compute_weighted_prime_count(
    primes: List[Action],
    X_max: int = 100
) -> np.ndarray:
    """
    Compute weighted prime count Π_w(x) using fuzzy severities.
    
    Instead of counting primes, we sum their severities.
    
    Parameters
    ----------
    primes : List[Action]
        List of ethical primes (with severity assigned)
    X_max : int, default=100
        Maximum complexity
        
    Returns
    -------
    np.ndarray
        Weighted count Π_w(x) for x in [1, X_max]
    """
    x_values = np.arange(1, X_max + 1)
    Pi_w = np.zeros(X_max, dtype=float)
    
    for prime in primes:
        if prime.c <= X_max:
            severity = getattr(prime, 'severity', 1.0)  # Default to 1.0 if not set
            for i, x in enumerate(x_values):
                if prime.c <= x:
                    Pi_w[i] += severity
    
    return Pi_w


def compare_crisp_vs_fuzzy(
    actions: List[Action],
    tau: float = 0.3,
    membership_type: str = 'triangular'
) -> dict:
    """
    Compare crisp (binary) vs fuzzy (continuous) error assessment.
    
    Parameters
    ----------
    actions : List[Action]
        Actions to compare
    tau : float, default=0.3
        Threshold
    membership_type : str, default='triangular'
        Fuzzy membership type
        
    Returns
    -------
    dict
        Comparison metrics
    """
    # Crisp assessment
    crisp_mistakes = sum(1 for a in actions if a.mistake_flag == 1)
    crisp_error_rate = crisp_mistakes / len(actions) if len(actions) > 0 else 0.0
    
    # Fuzzy assessment
    assign_fuzzy_severities(actions, tau=tau, membership_type=membership_type)
    fuzzy_total_severity = sum(getattr(a, 'severity', 0.0) for a in actions)
    fuzzy_avg_severity = fuzzy_total_severity / len(actions) if len(actions) > 0 else 0.0
    
    # Count "significant" errors (severity > 0.5)
    fuzzy_significant = sum(1 for a in actions if getattr(a, 'severity', 0.0) > 0.5)
    
    return {
        'crisp_mistakes': crisp_mistakes,
        'crisp_error_rate': crisp_error_rate,
        'fuzzy_total_severity': fuzzy_total_severity,
        'fuzzy_avg_severity': fuzzy_avg_severity,
        'fuzzy_significant': fuzzy_significant,
        'difference': fuzzy_significant - crisp_mistakes,
        'relative_difference': (fuzzy_significant - crisp_mistakes) / max(crisp_mistakes, 1)
    }

