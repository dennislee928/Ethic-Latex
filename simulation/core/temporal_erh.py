"""
Temporal ERH Module

This module extends the Ethical Riemann Hypothesis to include time dimension,
enabling dynamic tracking of error evolution and prediction of future trends.

Key concepts:
- Π(x,t): Count of ethical primes up to complexity x at time t
- E(x,t): Error term as a function of both complexity and time
- Mule effect: Sudden anomalies that disrupt predictions (analogous to Asimov's Mule)
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Callable
from scipy import stats
from .action_space import Action
from .ethical_primes import select_ethical_primes, compute_Pi_and_error
from .judgement_system import BaseJudge, evaluate_judgement


def compute_Pi_temporal(
    primes_history: List[List[Action]],
    time_steps: int,
    X_max: int = 100
) -> np.ndarray:
    """
    Compute Π(x,t) - the count of ethical primes up to complexity x at time t.
    
    Parameters
    ----------
    primes_history : List[List[Action]]
        List of ethical primes at each time step
        primes_history[t] = list of primes at time t
    time_steps : int
        Number of time steps
    X_max : int, default=100
        Maximum complexity to consider
        
    Returns
    -------
    np.ndarray
        2D array of shape (time_steps, X_max)
        Pi_xt[t, x-1] = count of primes with complexity <= x at time t
        (x-1 because array is 0-indexed but complexity starts at 1)
        
    Examples
    --------
    >>> primes_t0 = [Action(id=1, c=10, V=0.5, w=1.0), ...]
    >>> primes_t1 = [Action(id=2, c=15, V=0.3, w=1.0), ...]
    >>> primes_history = [primes_t0, primes_t1]
    >>> Pi_xt = compute_Pi_temporal(primes_history, time_steps=2, X_max=100)
    >>> print(Pi_xt[0, 9])  # Count at t=0, x=10
    """
    Pi_xt = np.zeros((time_steps, X_max), dtype=float)
    
    for t in range(time_steps):
        if t < len(primes_history):
            primes_t = primes_history[t]
            # Count primes up to each complexity level
            for x in range(1, X_max + 1):
                count = sum(1 for p in primes_t if p.c <= x)
                Pi_xt[t, x - 1] = count
    
    return Pi_xt


def compute_E_temporal(
    Pi_xt: np.ndarray,
    B_xt: np.ndarray,
    time_steps: int,
    X_max: int = 100
) -> np.ndarray:
    """
    Compute E(x,t) = Π(x,t) - B(x,t) - the temporal error term.
    
    Parameters
    ----------
    Pi_xt : np.ndarray
        2D array of shape (time_steps, X_max) from compute_Pi_temporal
    B_xt : np.ndarray
        2D array of shape (time_steps, X_max) - baseline expectation at each time
        Can be computed from baseline function or fitted model
    time_steps : int
        Number of time steps
    X_max : int, default=100
        Maximum complexity
        
    Returns
    -------
    np.ndarray
        2D array of shape (time_steps, X_max)
        E_xt[t, x-1] = error at time t, complexity x
        
    Examples
    --------
    >>> Pi_xt = compute_Pi_temporal(primes_history, time_steps=10, X_max=100)
    >>> B_xt = compute_baseline_temporal(time_steps=10, X_max=100)
    >>> E_xt = compute_E_temporal(Pi_xt, B_xt, time_steps=10, X_max=100)
    """
    E_xt = Pi_xt - B_xt
    return E_xt


def compute_baseline_temporal(
    time_steps: int,
    X_max: int = 100,
    baseline_type: str = 'prime_theorem',
    baseline_params: Optional[Dict] = None,
    time_dependent: bool = False
) -> np.ndarray:
    """
    Compute baseline B(x,t) for temporal ERH.
    
    Parameters
    ----------
    time_steps : int
        Number of time steps
    X_max : int, default=100
        Maximum complexity
    baseline_type : str, default='prime_theorem'
        Type of baseline: 'linear', 'prime_theorem', 'logarithmic_integral', 'power_law'
    baseline_params : Optional[Dict], default=None
        Parameters for baseline function
    time_dependent : bool, default=False
        If True, baseline can change over time (e.g., drift)
        
    Returns
    -------
    np.ndarray
        2D array of shape (time_steps, X_max)
    """
    B_xt = np.zeros((time_steps, X_max), dtype=float)
    x_values = np.arange(1, X_max + 1)
    
    # Default parameters
    if baseline_params is None:
        if baseline_type == 'linear':
            baseline_params = {'alpha': 0.1}
        elif baseline_type == 'prime_theorem':
            baseline_params = {'beta': 10.0}
        elif baseline_type == 'logarithmic_integral':
            baseline_params = {'beta': 8.0}
        elif baseline_type == 'power_law':
            baseline_params = {'gamma': 0.5, 'delta': 0.8}
    
    for t in range(time_steps):
        # Time-dependent factor (optional drift)
        time_factor = 1.0
        if time_dependent:
            # Small linear drift over time
            time_factor = 1.0 + 0.01 * t / time_steps
        
        if baseline_type == 'linear':
            alpha = baseline_params.get('alpha', 0.1)
            B_xt[t, :] = alpha * x_values * time_factor
        elif baseline_type == 'prime_theorem':
            beta = baseline_params.get('beta', 10.0)
            # Avoid division by zero
            log_x = np.log(np.maximum(x_values, 2))
            B_xt[t, :] = beta * x_values / log_x * time_factor
        elif baseline_type == 'logarithmic_integral':
            beta = baseline_params.get('beta', 8.0)
            # Approximate Li(x) ≈ x / log(x) for large x
            log_x = np.log(np.maximum(x_values, 2))
            B_xt[t, :] = beta * x_values / log_x * time_factor
        elif baseline_type == 'power_law':
            gamma = baseline_params.get('gamma', 0.5)
            delta = baseline_params.get('delta', 0.8)
            B_xt[t, :] = gamma * (x_values ** delta) * time_factor
    
    return B_xt


def track_error_evolution(
    actions_history: List[List[Action]],
    judge: BaseJudge,
    tau: float = 0.3,
    time_steps: int = 10,
    X_max: int = 100,
    importance_quantile: float = 0.9
) -> Dict[str, np.ndarray]:
    """
    Track error evolution over time by evaluating actions at each time step.
    
    Parameters
    ----------
    actions_history : List[List[Action]]
        List of action sets at each time step
        actions_history[t] = list of actions at time t
    judge : BaseJudge
        Judgment system to evaluate actions
    tau : float, default=0.3
        Error threshold for misjudgment
    time_steps : int, default=10
        Number of time steps
    X_max : int, default=100
        Maximum complexity
    importance_quantile : float, default=0.9
        Quantile for selecting ethical primes
        
    Returns
    -------
    Dict[str, np.ndarray]
        Dictionary containing:
        - 'Pi_xt': Π(x,t) array
        - 'B_xt': B(x,t) baseline array
        - 'E_xt': E(x,t) error array
        - 'primes_history': List of primes at each time step
        
    Examples
    --------
    >>> judge = BiasedJudge(bias_strength=0.2)
    >>> actions_t0 = generate_world(1000, random_seed=42)
    >>> actions_t1 = generate_world(1000, random_seed=43)
    >>> actions_history = [actions_t0, actions_t1]
    >>> results = track_error_evolution(actions_history, judge, tau=0.3, time_steps=2)
    >>> E_xt = results['E_xt']
    """
    primes_history = []
    
    # Evaluate actions and select primes at each time step
    for t in range(min(time_steps, len(actions_history))):
        actions_t = actions_history[t].copy()
        evaluate_judgement(actions_t, judge, tau=tau)
        primes_t = select_ethical_primes(
            actions_t,
            importance_quantile=importance_quantile
        )
        primes_history.append(primes_t)
    
    # Compute temporal functions
    Pi_xt = compute_Pi_temporal(primes_history, time_steps, X_max)
    
    # Compute baseline (can be improved with actual fitting)
    B_xt = compute_baseline_temporal(time_steps, X_max)
    
    # Compute error
    E_xt = compute_E_temporal(Pi_xt, B_xt, time_steps, X_max)
    
    return {
        'Pi_xt': Pi_xt,
        'B_xt': B_xt,
        'E_xt': E_xt,
        'primes_history': primes_history,
        'time_steps': time_steps,
        'X_max': X_max
    }


def simulate_mule_effect(
    E_xt: np.ndarray,
    mule_time: int,
    mule_strength: float = 2.0,
    mule_complexity_range: Optional[Tuple[int, int]] = None,
    X_max: int = 100
) -> np.ndarray:
    """
    Simulate the "Mule effect" - sudden anomalies that disrupt predictions.
    
    In Asimov's Foundation series, the Mule is an unpredictable individual
    who disrupts psychohistory's predictions. Here, we simulate similar
    sudden jumps in error that exceed normal ERH bounds.
    
    Parameters
    ----------
    E_xt : np.ndarray
        Original error array of shape (time_steps, X_max)
    mule_time : int
        Time step at which the Mule effect occurs
    mule_strength : float, default=2.0
        Multiplier for error magnitude (higher = more disruptive)
    mule_complexity_range : Optional[Tuple[int, int]], default=None
        Complexity range affected by Mule. If None, affects all complexities
    X_max : int, default=100
        Maximum complexity
        
    Returns
    -------
    np.ndarray
        Modified error array with Mule effect applied
        
    Examples
    --------
    >>> E_xt = compute_E_temporal(Pi_xt, B_xt, time_steps=10, X_max=100)
    >>> E_xt_mule = simulate_mule_effect(E_xt, mule_time=5, mule_strength=3.0)
    """
    E_xt_modified = E_xt.copy()
    time_steps = E_xt.shape[0]
    
    if mule_time >= time_steps:
        return E_xt_modified
    
    # Determine affected complexity range
    if mule_complexity_range is None:
        # Affect mid-to-high complexity (where errors matter most)
        min_c = X_max // 3
        max_c = X_max
    else:
        min_c, max_c = mule_complexity_range
    
    # Apply Mule effect: sudden jump in error
    for x_idx in range(min_c - 1, min(max_c, X_max)):
        # Create a sudden spike that violates ERH bounds
        base_error = E_xt[mule_time, x_idx]
        mule_error = base_error * mule_strength
        
        # Add random direction (can be positive or negative)
        direction = np.random.choice([-1, 1])
        E_xt_modified[mule_time, x_idx] = direction * abs(mule_error)
        
        # Ripple effect to subsequent time steps (decay)
        for t in range(mule_time + 1, min(mule_time + 3, time_steps)):
            decay_factor = 0.5 ** (t - mule_time)
            E_xt_modified[t, x_idx] += direction * abs(mule_error) * decay_factor * 0.3
    
    return E_xt_modified


def detect_mule_anomalies(
    E_xt: np.ndarray,
    C: float = 1.0,
    epsilon: float = 0.1,
    threshold_multiplier: float = 1.5,
    X_max: int = 100
) -> List[Dict]:
    """
    Detect potential "Mule" anomalies - sudden jumps that violate ERH bounds.
    
    Parameters
    ----------
    E_xt : np.ndarray
        Error array of shape (time_steps, X_max)
    C : float, default=1.0
        ERH constant
    epsilon : float, default=0.1
        ERH epsilon parameter
    threshold_multiplier : float, default=1.5
        Multiplier for anomaly detection (1.5 = 50% above ERH bound)
    X_max : int, default=100
        Maximum complexity
        
    Returns
    -------
    List[Dict]
        List of detected anomalies, each containing:
        - 'time': time step
        - 'complexity': complexity level
        - 'error_magnitude': |E(x,t)|
        - 'erh_bound': ERH bound at that point
        - 'violation_ratio': how much it exceeds the bound
        
    Examples
    --------
    >>> E_xt = compute_E_temporal(Pi_xt, B_xt, time_steps=10, X_max=100)
    >>> anomalies = detect_mule_anomalies(E_xt, C=1.0, epsilon=0.1)
    >>> for anomaly in anomalies:
    ...     print(f"Mule detected at t={anomaly['time']}, x={anomaly['complexity']}")
    """
    anomalies = []
    time_steps = E_xt.shape[0]
    x_values = np.arange(1, X_max + 1)
    
    for t in range(time_steps):
        for x_idx, x in enumerate(x_values):
            error_mag = abs(E_xt[t, x_idx])
            
            # ERH bound: C * x^(1/2 + epsilon)
            erh_bound = C * (x ** (0.5 + epsilon))
            threshold = erh_bound * threshold_multiplier
            
            if error_mag > threshold:
                violation_ratio = error_mag / erh_bound
                anomalies.append({
                    'time': t,
                    'complexity': x,
                    'error_magnitude': error_mag,
                    'erh_bound': erh_bound,
                    'violation_ratio': violation_ratio,
                    'error_value': E_xt[t, x_idx]
                })
    
    return anomalies


def add_stochastic_perturbation(
    E_xt: np.ndarray,
    noise_scale: float = 0.1,
    correlation_time: int = 2
) -> np.ndarray:
    """
    Add stochastic perturbation to simulate random fluctuations.
    
    Parameters
    ----------
    E_xt : np.ndarray
        Original error array
    noise_scale : float, default=0.1
        Standard deviation of noise
    correlation_time : int, default=2
        Time correlation (how many steps noise persists)
        
    Returns
    -------
    np.ndarray
        Error array with stochastic perturbation
    """
    E_xt_perturbed = E_xt.copy()
    time_steps, X_max = E_xt.shape
    
    # Generate correlated noise
    noise = np.zeros((time_steps, X_max))
    for t in range(time_steps):
        if t == 0:
            noise[t, :] = np.random.normal(0, noise_scale, X_max)
        else:
            # Correlated with previous time step
            decay = np.exp(-1.0 / correlation_time)
            noise[t, :] = (decay * noise[t-1, :] + 
                          np.random.normal(0, noise_scale * (1 - decay), X_max))
    
    E_xt_perturbed += noise
    return E_xt_perturbed


