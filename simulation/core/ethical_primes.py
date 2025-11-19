"""
Ethical Primes Module

This module implements the concept of "ethical primes" - critical misjudgments
that represent fundamental errors in moral judgment systems.

It also computes Π(x), B(x), and E(x) functions analogous to the prime counting
function and error terms in number theory.
"""

import numpy as np
from typing import List, Tuple, Literal, Optional
from scipy.optimize import curve_fit
from .action_space import Action


def select_ethical_primes(
    actions: List[Action],
    importance_quantile: float = 0.9,
    strategy: Literal['importance', 'complexity', 'hybrid'] = 'importance',
    complexity_range: Optional[Tuple[int, int]] = None
) -> List[Action]:
    """
    Select "ethical primes" from the set of misjudged actions.
    
    Ethical primes are defined as critical misjudgments - cases that:
    1. Are actually misjudged (mistake_flag = 1)
    2. Have high importance (affect many people, high stakes)
    3. Fall within a meaningful complexity range (not trivial, not impossibly complex)
    
    Parameters
    ----------
    actions : List[Action]
        List of actions that have been judged
    importance_quantile : float, default=0.9
        Keep only top (1 - quantile) by importance
        E.g., 0.9 keeps top 10% most important
    strategy : {'importance', 'complexity', 'hybrid'}, default='importance'
        Selection strategy:
        - 'importance': Select by importance weight only
        - 'complexity': Prefer mid-range complexity
        - 'hybrid': Balance importance and complexity
    complexity_range : Optional[Tuple[int, int]], default=None
        If specified, only include actions with c in [min_c, max_c]
        If None, automatically set to exclude bottom 10% and top 10%
        
    Returns
    -------
    List[Action]
        Subset of actions identified as "ethical primes"
        
    Examples
    --------
    >>> actions = generate_world(1000)
    >>> judge = BiasedJudge()
    >>> evaluate_judgement(actions, judge, tau=0.3)
    >>> primes = select_ethical_primes(actions, importance_quantile=0.9)
    >>> print(f"Found {len(primes)} ethical primes")
    
    Notes
    -----
    The analogy with mathematical primes:
    - Not all misjudgments are "primes" - only the structurally important ones
    - Primes represent fundamental errors that can't be reduced to simpler cases
    - Their distribution tells us about the "health" of the judgment system
    """
    # Filter to only misjudgments
    mistakes = [a for a in actions if a.mistake_flag == 1]
    
    if len(mistakes) == 0:
        return []
    
    # Apply complexity range filter
    if complexity_range is not None:
        min_c, max_c = complexity_range
        mistakes = [a for a in mistakes if min_c <= a.c <= max_c]
    else:
        # Auto range: exclude bottom 10% and top 10% complexity
        all_complexities = sorted([a.c for a in mistakes])
        if len(all_complexities) >= 10:
            min_c = all_complexities[len(all_complexities) // 10]
            max_c = all_complexities[9 * len(all_complexities) // 10]
            mistakes = [a for a in mistakes if min_c <= a.c <= max_c]
    
    if len(mistakes) == 0:
        return []
    
    # Select by strategy
    if strategy == 'importance':
        # Sort by importance and take top quantile
        mistakes.sort(key=lambda a: a.w, reverse=True)
        cutoff_idx = int(len(mistakes) * (1 - importance_quantile))
        primes = mistakes[:max(cutoff_idx, 1)]
        
    elif strategy == 'complexity':
        # Prefer mid-range complexity (most interesting cases)
        # Score by distance from median complexity
        complexities = [a.c for a in mistakes]
        median_c = np.median(complexities)
        
        # Score: high importance, moderate complexity deviation
        def score(a):
            c_score = 1.0 / (1.0 + abs(a.c - median_c) / median_c)
            w_score = a.w / max(act.w for act in mistakes)
            return 0.3 * c_score + 0.7 * w_score
        
        mistakes.sort(key=score, reverse=True)
        cutoff_idx = int(len(mistakes) * (1 - importance_quantile))
        primes = mistakes[:max(cutoff_idx, 1)]
        
    elif strategy == 'hybrid':
        # Balance importance and error magnitude
        max_w = max(a.w for a in mistakes)
        max_delta = max(abs(a.delta) for a in mistakes) if mistakes else 1.0
        
        def score(a):
            w_normalized = a.w / max_w
            delta_normalized = abs(a.delta) / max_delta
            return 0.7 * w_normalized + 0.3 * delta_normalized
        
        mistakes.sort(key=score, reverse=True)
        cutoff_idx = int(len(mistakes) * (1 - importance_quantile))
        primes = mistakes[:max(cutoff_idx, 1)]
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    return primes


def compute_Pi_and_error(
    primes: List[Action],
    X_max: int = 100,
    baseline: Literal['linear', 'prime_theorem', 'fitted'] = 'prime_theorem',
    baseline_params: Optional[dict] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute Π(x), B(x), and E(x) = Π(x) - B(x).
    
    This is the core function for the Ethical Riemann Hypothesis analog.
    
    Parameters
    ----------
    primes : List[Action]
        List of ethical primes
    X_max : int, default=100
        Maximum complexity to consider
    baseline : {'linear', 'prime_theorem', 'fitted'}, default='prime_theorem'
        Type of baseline function B(x):
        - 'linear': B(x) = α * x
        - 'prime_theorem': B(x) = β * x / log(x), analogous to Li(x)
        - 'fitted': Fit a smooth curve to Π(x)
    baseline_params : Optional[dict], default=None
        Parameters for baseline function
        - For 'linear': {'alpha': float}
        - For 'prime_theorem': {'beta': float}
        - For 'fitted': automatic fitting
        
    Returns
    -------
    Pi_x : np.ndarray
        Π(x) values - count of ethical primes up to complexity x
    B_x : np.ndarray
        B(x) values - baseline expectation
    E_x : np.ndarray
        E(x) values - error term E(x) = Π(x) - B(x)
    x_values : np.ndarray
        Array of x values from 1 to X_max
        
    Examples
    --------
    >>> primes = select_ethical_primes(actions)
    >>> Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
    >>> import matplotlib.pyplot as plt
    >>> plt.plot(x_vals, E_x)
    >>> plt.xlabel('Complexity x')
    >>> plt.ylabel('Error E(x)')
    >>> plt.show()
    
    Notes
    -----
    The Ethical Riemann Hypothesis (ERH) states that:
    |E(x)| ≤ C * x^(1/2 + ε) for some constants C, ε > 0
    
    This function computes E(x) so we can test whether this bound holds.
    """
    x_values = np.arange(1, X_max + 1)
    Pi_x = np.zeros(X_max, dtype=float)
    
    # Compute Π(x): count of primes up to complexity x
    prime_complexities = [p.c for p in primes if p.c <= X_max]
    
    for i, x in enumerate(x_values):
        Pi_x[i] = sum(1 for c in prime_complexities if c <= x)
    
    # Compute baseline B(x)
    if baseline == 'linear':
        alpha = baseline_params.get('alpha', 0.1) if baseline_params else 0.1
        B_x = alpha * x_values
        
    elif baseline == 'prime_theorem':
        # B(x) = β * x / log(x), analogous to Prime Number Theorem
        beta = baseline_params.get('beta', 1.0) if baseline_params else 1.0
        
        # Avoid log(1) = 0
        B_x = np.zeros_like(x_values, dtype=float)
        for i, x in enumerate(x_values):
            if x > 1:
                B_x[i] = beta * x / np.log(x)
            else:
                B_x[i] = 0
                
    elif baseline == 'fitted':
        # Fit a smooth polynomial to Π(x)
        if len(primes) < 5:
            # Not enough data, fall back to linear
            B_x = 0.1 * x_values
        else:
            # Fit a degree-3 polynomial
            degree = min(3, len(primes) // 2)
            coeffs = np.polyfit(x_values, Pi_x, degree)
            B_x = np.polyval(coeffs, x_values)
    else:
        raise ValueError(f"Unknown baseline type: {baseline}")
    
    # Compute error
    E_x = Pi_x - B_x
    
    return Pi_x, B_x, E_x, x_values


def analyze_error_growth(
    E_x: np.ndarray,
    x_values: np.ndarray,
    expected_exponent: float = 0.5
) -> dict:
    """
    Analyze whether |E(x)| grows like x^α and estimate α.
    
    This tests the Ethical Riemann Hypothesis by checking if α ≈ 0.5.
    
    Parameters
    ----------
    E_x : np.ndarray
        Error values
    x_values : np.ndarray
        Complexity values
    expected_exponent : float, default=0.5
        Expected growth exponent (0.5 for ERH)
        
    Returns
    -------
    dict
        Analysis results including:
        - 'estimated_exponent': fitted α value
        - 'erh_satisfied': whether |α - 0.5| < 0.1
        - 'r_squared': goodness of fit
        - 'max_absolute_error': max |E(x)|
        - 'growth_rate': how E(x) grows
        
    Examples
    --------
    >>> Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes)
    >>> analysis = analyze_error_growth(E_x, x_vals)
    >>> print(f"Estimated exponent: {analysis['estimated_exponent']:.3f}")
    >>> print(f"ERH satisfied: {analysis['erh_satisfied']}")
    """
    # Filter out zeros and take absolute value
    abs_E = np.abs(E_x)
    valid_mask = (abs_E > 0) & (x_values > 1)
    
    if np.sum(valid_mask) < 5:
        return {
            'estimated_exponent': np.nan,
            'erh_satisfied': False,
            'r_squared': 0.0,
            'max_absolute_error': np.max(abs_E) if len(abs_E) > 0 else 0,
            'growth_rate': 'insufficient_data'
        }
    
    x_valid = x_values[valid_mask]
    E_valid = abs_E[valid_mask]
    
    # Fit |E(x)| = C * x^α using log-log regression
    # log|E(x)| = log(C) + α * log(x)
    log_x = np.log(x_valid)
    log_E = np.log(E_valid)
    
    # Linear regression in log space
    coeffs = np.polyfit(log_x, log_E, 1)
    alpha = coeffs[0]  # slope = exponent
    log_C = coeffs[1]  # intercept = log(C)
    
    # Compute R² for goodness of fit
    log_E_pred = np.polyval(coeffs, log_x)
    ss_res = np.sum((log_E - log_E_pred)**2)
    ss_tot = np.sum((log_E - np.mean(log_E))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # Check if ERH is satisfied
    erh_satisfied = abs(alpha - expected_exponent) < 0.15
    
    # Classify growth rate
    if alpha < 0.4:
        growth_rate = 'sublinear_slow'  # Better than ERH!
    elif 0.4 <= alpha < 0.6:
        growth_rate = 'square_root'  # Consistent with ERH
    elif 0.6 <= alpha < 0.9:
        growth_rate = 'sublinear_fast'
    elif 0.9 <= alpha < 1.1:
        growth_rate = 'linear'
    else:
        growth_rate = 'superlinear'  # Problematic!
    
    return {
        'estimated_exponent': alpha,
        'constant_C': np.exp(log_C),
        'erh_satisfied': erh_satisfied,
        'r_squared': r_squared,
        'max_absolute_error': np.max(abs_E),
        'mean_absolute_error': np.mean(abs_E),
        'growth_rate': growth_rate,
        'deviation_from_erh': abs(alpha - expected_exponent)
    }


def compare_error_distributions(
    results: dict,
    X_max: int = 100
) -> dict:
    """
    Compare error distributions across multiple judges.
    
    Parameters
    ----------
    results : dict
        Dictionary mapping judge names to lists of evaluated actions
        (output from batch_evaluate)
    X_max : int, default=100
        Maximum complexity
        
    Returns
    -------
    dict
        Comparison results for each judge
    """
    comparison = {}
    
    for name, actions in results.items():
        primes = select_ethical_primes(actions)
        if len(primes) == 0:
            comparison[name] = {'error': 'no_primes'}
            continue
            
        Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=X_max)
        analysis = analyze_error_growth(E_x, x_vals)
        
        comparison[name] = {
            'num_primes': len(primes),
            'Pi_x': Pi_x,
            'B_x': B_x,
            'E_x': E_x,
            'x_values': x_vals,
            'analysis': analysis
        }
    
    return comparison


def compute_prime_density(
    primes: List[Action],
    X_max: int = 100,
    bin_size: int = 5
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the density of ethical primes in complexity bins.
    
    Parameters
    ----------
    primes : List[Action]
        List of ethical primes
    X_max : int, default=100
        Maximum complexity
    bin_size : int, default=5
        Size of complexity bins
        
    Returns
    -------
    bin_centers : np.ndarray
        Center of each bin
    densities : np.ndarray
        Number of primes per bin
    """
    bins = np.arange(0, X_max + bin_size, bin_size)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    prime_complexities = [p.c for p in primes if p.c <= X_max]
    densities, _ = np.histogram(prime_complexities, bins=bins)
    
    return bin_centers, densities

