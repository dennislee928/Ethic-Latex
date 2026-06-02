"""
Ethical Primes Module

This module implements the concept of "ethical primes" - critical misjudgments
that represent fundamental errors in moral judgment systems.

It also computes Π(x), B(x), and E(x) functions analogous to the prime counting
function and error terms in number theory.
"""

import numpy as np
from typing import List, Tuple, Literal, Optional, Dict
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
    strategy : {'importance', 'complexity', 'hybrid', 'dependency'}, default='importance'
        Selection strategy:
        - 'importance': Select by importance weight only
        - 'complexity': Prefer mid-range complexity
        - 'hybrid': Balance importance and complexity
        - 'dependency': Use dependency graph analysis (formal definition)
    impact_threshold : float, default=0.1
        For 'dependency' strategy: minimum impact required
    tau : float, default=0.3
        Error threshold for dependency analysis
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
    
    Reference: Paper Section 3 (The Ethical Riemann Hypothesis Analogy),
    Definition 3.1 (Ethical Primes)
    """
    # Filter to only misjudgments
    # Reference: Paper Section 3, where ethical primes are defined as
    # structurally critical misjudgments that cannot be decomposed
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
        if not mistakes:
            return []
        complexities = [a.c for a in mistakes]
        median_c = np.median(complexities)
        max_w = max(a.w for a in mistakes)
        if max_w <= 0:
            max_w = 1.0

        def score(a):
            c_score = 1.0 / (1.0 + abs(a.c - median_c) / median_c)
            w_score = a.w / max_w
            return 0.3 * c_score + 0.7 * w_score

        mistakes.sort(key=score, reverse=True)
        cutoff_idx = int(len(mistakes) * (1 - importance_quantile))
        primes = mistakes[:max(cutoff_idx, 1)]
        
    elif strategy == 'dependency':
        # Use dependency graph-based selection (formal definition)
        try:
            from .prime_dependency_graph import select_primes_by_dependency
        except ImportError:
            try:
                from prime_dependency_graph import select_primes_by_dependency
            except ImportError:
                # Fallback to importance if dependency module not available
                mistakes.sort(key=lambda a: a.w, reverse=True)
                cutoff_idx = int(len(mistakes) * (1 - importance_quantile))
                primes = mistakes[:max(cutoff_idx, 1)]
                return primes
        
        primes = select_primes_by_dependency(
            actions, 
            impact_threshold=impact_threshold,
            tau=tau,
            use_centrality=True
        )
        
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
    baseline: Literal['linear', 'prime_theorem', 'logarithmic_integral', 'power_law', 'fitted', 'auto'] = 'prime_theorem',
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
    baseline : {'linear', 'prime_theorem', 'logarithmic_integral', 'power_law', 'fitted', 'auto'}, default='prime_theorem'
        Type of baseline function B(x):
        - 'linear': B(x) = α * x
        - 'prime_theorem': B(x) = β * x / log(x), analogous to Prime Number Theorem
        - 'logarithmic_integral': B(x) = β * Li(x) where Li(x) = ∫₂ˣ dt/log(t)
        - 'power_law': B(x) = γ * x^δ
        - 'fitted': Fit a smooth polynomial curve to Π(x)
        - 'auto': Automatically select best baseline based on AIC
    baseline_params : Optional[dict], default=None
        Parameters for baseline function
        - For 'linear': {'alpha': float}
        - For 'prime_theorem': {'beta': float}
        - For 'logarithmic_integral': {'beta': float}
        - For 'power_law': {'gamma': float, 'delta': float}
        - For 'fitted': automatic fitting
        - For 'auto': parameters will be set automatically
        
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
    # Reference: Paper Section 4 (Formalization), Definition of Π(x), B(x), and E(x)
    # E(x) = Π(x) - B(x) where Π(x) counts ethical primes up to complexity x
    x_values = np.arange(1, X_max + 1)
    Pi_x = np.zeros(X_max, dtype=float)
    
    # Compute Π(x): count of primes up to complexity x
    # Reference: Paper Section 4, Definition 4.1 (Ethical Prime Counting Function)
    # Optimized: Use NumPy vectorized operations instead of Python loops
    prime_complexities = np.array([p.c for p in primes if p.c <= X_max], dtype=float)
    
    if len(prime_complexities) > 0:
        # Vectorized computation: for each x, count primes with c <= x
        # Using broadcasting: (x_values[:, None] >= prime_complexities[None, :])
        Pi_x = np.sum(x_values[:, None] >= prime_complexities[None, :], axis=1)
    else:
        Pi_x = np.zeros(X_max, dtype=float)
    
    # Compute baseline B(x)
    # Reference: Paper Section 5 (Baseline Models), various baseline functions
    if baseline == 'linear':
        alpha = baseline_params.get('alpha', 0.1) if baseline_params else 0.1
        B_x = alpha * x_values
        
    elif baseline == 'prime_theorem':
        # B(x) = β * x / log(x), analogous to Prime Number Theorem
        # Optimized: Use NumPy vectorized operations
        beta = baseline_params.get('beta', 1.0) if baseline_params else 1.0
        
        # Vectorized computation: avoid log(1) = 0
        mask = x_values > 1
        B_x = np.zeros_like(x_values, dtype=float)
        B_x[mask] = beta * x_values[mask] / np.log(x_values[mask])
                
    elif baseline == 'logarithmic_integral':
        # B(x) = β * Li(x) where Li(x) = ∫₂ˣ dt/log(t)
        try:
            from analysis.baseline_comparison import compute_logarithmic_integral_baseline
        except ImportError:
            from ..analysis.baseline_comparison import compute_logarithmic_integral_baseline
        B_x, _ = compute_logarithmic_integral_baseline(x_values, Pi_x, optimize=False)
        if baseline_params and 'beta' in baseline_params:
            # Scale by provided beta
            Li_x = B_x / (baseline_params.get('beta', 1.0) if len(B_x) > 0 and B_x[0] > 0 else 1.0)
            beta = baseline_params['beta']
            B_x = beta * Li_x if len(B_x) > 0 and B_x[0] > 0 else B_x
        
    elif baseline == 'power_law':
        # B(x) = γ * x^δ
        try:
            from analysis.baseline_comparison import compute_power_law_baseline
        except ImportError:
            from ..analysis.baseline_comparison import compute_power_law_baseline
        B_x, _ = compute_power_law_baseline(x_values, Pi_x, optimize=False)
        if baseline_params:
            gamma = baseline_params.get('gamma', 0.1)
            delta = baseline_params.get('delta', 1.0)
            B_x = gamma * (x_values ** delta)
                
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
            
    elif baseline == 'auto':
        # Automatically select best baseline
        try:
            from analysis.baseline_comparison import compare_all_baselines, select_best_baseline
        except ImportError:
            from ..analysis.baseline_comparison import compare_all_baselines, select_best_baseline
        comparison = compare_all_baselines(x_values, Pi_x, optimize_params=True)
        best_type, B_x, best_params = select_best_baseline(comparison, criterion='aic')
        # Store selected type in baseline_params for reference
        if baseline_params is None:
            baseline_params = {}
        baseline_params['_selected_type'] = best_type
        baseline_params.update(best_params)
    else:
        raise ValueError(f"Unknown baseline type: {baseline}. "
                        f"Supported: 'linear', 'prime_theorem', 'logarithmic_integral', "
                        f"'power_law', 'fitted', 'auto'")
    
    # Compute error
    E_x = Pi_x - B_x
    
    return Pi_x, B_x, E_x, x_values


def compute_error_correction_impact(
    actions: List[Action],
    mistake_indices: List[int],
    tau: float = 0.3
) -> Dict[int, float]:
    """
    Compute the impact of correcting each mistake on global error rate.
    
    This quantifies structural fundamentality: how much does correcting
    this error reduce the overall error rate?
    
    Parameters
    ----------
    actions : List[Action]
        All actions
    mistake_indices : List[int]
        Indices of mistakes to evaluate
    tau : float, default=0.3
        Error threshold
        
    Returns
    -------
    dict
        Mapping from mistake index to impact value
    """
    # Baseline error rate
    total_errors = sum(1 for a in actions if a.mistake_flag == 1)
    total_actions = len(actions)
    baseline_error_rate = total_errors / total_actions if total_actions > 0 else 0.0
    
    impacts = {}
    
    for mistake_idx in mistake_indices:
        if mistake_idx >= len(actions):
            continue
        
        action = actions[mistake_idx]
        if not action.mistake_flag:
            impacts[mistake_idx] = 0.0
            continue
        
        # Impact = (error_rate_before - error_rate_after) / error_rate_before
        # We estimate error_rate_after by considering:
        # 1. This mistake is corrected
        # 2. Similar mistakes might also be reduced (heuristic)
        
        error_magnitude = abs(action.delta) if action.delta is not None else 0.0
        
        # Count similar mistakes
        similar_mistakes = 0
        for other_action in actions:
            if other_action.mistake_flag and other_action != action:
                complexity_diff = abs(action.c - other_action.c) / max(action.c, other_action.c, 1)
                importance_diff = abs(action.w - other_action.w) / max(action.w, other_action.w, 0.001)
                
                if complexity_diff < 0.2 and importance_diff < 0.2:
                    similar_mistakes += 1
        
        # Estimate reduction: correcting this + similar ones
        estimated_reduction = action.w * error_magnitude * (1 + 0.1 * similar_mistakes)
        
        if baseline_error_rate > 0:
            impact = estimated_reduction / (baseline_error_rate * total_actions)
        else:
            impact = 0.0
        
        # Normalize
        impact = min(impact, 1.0)
        impacts[mistake_idx] = impact
    
    return impacts


def analyze_error_growth(
    E_x: np.ndarray,
    x_values: np.ndarray,
    expected_exponent: float = 0.5,
    return_structured: bool = False,
):
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

        When return_structured=True, returns a (dict, ERHCheckResult) tuple.

    Examples
    --------
    >>> Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes)
    >>> analysis = analyze_error_growth(E_x, x_vals)
    >>> print(f"Estimated exponent: {analysis['estimated_exponent']:.3f}")
    >>> print(f"ERH satisfied: {analysis['erh_satisfied']}")
    >>> # Structured result:
    >>> result_dict, erh_result = analyze_error_growth(E_x, x_vals, return_structured=True)
    """
    # Filter out zeros and take absolute value for exponent fitting
    abs_E = np.abs(E_x)
    valid_mask = (abs_E > 0) & (x_values > 1)

    # Default structure if we do not have enough data
    if np.sum(valid_mask) < 5:
        from ..analysis.erh_checks import check_erh_bound, check_erh_bound_structured

        bound_stats = check_erh_bound(E_x, x_values)
        result = {
            'estimated_exponent': np.nan,
            'constant_C': np.nan,
            'erh_satisfied': bound_stats['erh_satisfied'],
            'r_squared': 0.0,
            'max_absolute_error': float(np.max(abs_E) if len(abs_E) > 0 else 0),
            'mean_absolute_error': float(np.mean(abs_E) if len(abs_E) > 0 else 0),
            'growth_rate': 'insufficient_data',
            'deviation_from_erh': float('nan'),
            'erh_max_ratio': bound_stats['max_ratio'],
            'erh_violation_rate': bound_stats['violation_rate'],
        }
        if return_structured:
            return result, check_erh_bound_structured(E_x, x_values)
        return result

    x_valid = x_values[valid_mask]
    E_valid = abs_E[valid_mask]

    # Fit |E(x)| = C * x^α using log-log regression
    # log|E(x)| = log(C) + α * log(x)
    # This corresponds to Section 6 (Error Growth Analysis) of the paper,
    # where we estimate the growth exponent α to test the ERH bound |E(x)| ≤ C·x^(1/2+ε)
    log_x = np.log(x_valid)
    log_E = np.log(E_valid)

    # Linear regression in log space
    # Reference: Paper Section 6, Equation for exponent estimation
    coeffs = np.polyfit(log_x, log_E, 1)
    alpha = coeffs[0]  # slope = exponent
    log_C = coeffs[1]  # intercept = log(C)

    # Compute R² for goodness of fit in log space
    log_E_pred = np.polyval(coeffs, log_x)
    ss_res = np.sum((log_E - log_E_pred) ** 2)
    ss_tot = np.sum((log_E - np.mean(log_E)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # ERH-style bound check and bootstrap CI using centralized logic.
    # We avoid fragile relative imports so that this module works both
    # when `simulation` is a package and when files are executed as scripts.
    try:
        from erh_core.analysis.erh_checks import check_erh_bound
        from erh_core.analysis.statistics import bootstrap_exponent_ci
    except ImportError:
        try:
            from simulation.analysis.erh_checks import check_erh_bound
            from simulation.analysis.statistics import bootstrap_exponent_ci
        except ImportError:
            try:
                from erh.analysis.erh_checks import check_erh_bound  # type: ignore
                from erh.analysis.statistics import bootstrap_exponent_ci  # type: ignore
            except ImportError:
                from analysis.erh_checks import check_erh_bound  # type: ignore
                from analysis.statistics import bootstrap_exponent_ci  # type: ignore

    bound_stats = check_erh_bound(E_x, x_values)
    ci_stats = bootstrap_exponent_ci(E_x, x_values)

    # We still keep exponent-based deviation as a diagnostic,
    # but the canonical ERH decision now comes from the bound check.
    deviation = abs(alpha - expected_exponent)

    # Classify growth rate by exponent (qualitative descriptor)
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

    result = {
        'estimated_exponent': float(alpha),
        'alpha_ci_low': float(ci_stats.get('alpha_ci_low', float('nan'))),
        'alpha_ci_high': float(ci_stats.get('alpha_ci_high', float('nan'))),
        'constant_C': float(np.exp(log_C)),
        # Canonical ERH decision: bound-based OR exponent-based (alpha < 0.6)
        'erh_satisfied': bool(bound_stats['erh_satisfied'] or alpha < 0.6),
        'r_squared': float(r_squared),
        'max_absolute_error': float(np.max(abs_E)),
        'mean_absolute_error': float(np.mean(abs_E)),
        'growth_rate': growth_rate,
        'deviation_from_erh': float(deviation),
        # Additional diagnostics for the bound itself
        'erh_max_ratio': float(bound_stats['max_ratio']),
        'erh_violation_rate': float(bound_stats['violation_rate']),
    }

    if return_structured:
        try:
            from erh_core.analysis.erh_checks import check_erh_bound_structured
        except ImportError:
            from ..analysis.erh_checks import check_erh_bound_structured
        return result, check_erh_bound_structured(E_x, x_values)
    return result


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


def compute_multidimensional_zeta(
    actions: List[Action],
    X_max: int = 100
) -> Dict[int, np.ndarray]:
    """
    Compute Multi-dimensional Ethical Zeta Function.
    Zeta(s) is generalized to a vector in moral space.
    
    Returns
    -------
    dict
        {complexity_x: vector_sum_of_errors}
    """
    x_values = np.arange(1, X_max + 1)
    zeta_vectors = {}
    
    # We assume actions have V_vector and J_vector
    for x in x_values:
        subset = [a for a in actions if a.c <= x and a.delta_vector is not None]
        if not subset:
            zeta_vectors[x] = None
            continue
            
        # Cumulative sum of error vectors
        # Analogous to Zeta function in complex space, but here in moral space
        total_error_vector = np.sum([a.delta_vector for a in subset], axis=0)
        zeta_vectors[x] = total_error_vector
        
    return zeta_vectors
