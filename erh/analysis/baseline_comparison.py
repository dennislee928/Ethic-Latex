"""
Baseline Function Comparison Module

This module provides tools for comparing different baseline functions B(x)
and selecting the best one based on statistical fit metrics.

Baseline functions compared:
- Linear: B(x) = αx
- Prime Theorem: B(x) = βx/log(x)
- Logarithmic Integral: B(x) = Li(x) = ∫₂ˣ dt/log(t)
- Power Law: B(x) = γx^δ
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Literal
from scipy.optimize import curve_fit
from scipy.integrate import quad
from scipy.stats import pearsonr
import warnings


def logarithmic_integral(x: float) -> float:
    """
    Compute the logarithmic integral Li(x) = ∫₂ˣ dt/log(t).
    
    This is the standard form used in number theory, analogous to
    the prime counting function.
    
    Parameters
    ----------
    x : float
        Upper limit of integration
        
    Returns
    -------
    float
        Value of Li(x)
        
    Notes
    -----
    Li(x) is defined as the Cauchy principal value:
    Li(x) = lim_{ε→0} [∫_{2}^{1-ε} dt/log(t) + ∫_{1+ε}^{x} dt/log(t)]
    
    For x < 2, we return 0.
    """
    if x < 2:
        return 0.0
    
    def integrand(t):
        if t <= 1:
            return 0.0
        return 1.0 / np.log(t)
    
    try:
        # Use scipy's quad for numerical integration
        result, _ = quad(integrand, 2.0, x, limit=100)
        return result
    except (ValueError, OverflowError):
        # Fallback approximation for large x
        return x / np.log(x)


def compute_linear_baseline(
    x_values: np.ndarray,
    Pi_x: np.ndarray,
    optimize: bool = True
) -> Tuple[np.ndarray, Dict]:
    """
    Compute linear baseline B(x) = αx.
    
    Parameters
    ----------
    x_values : np.ndarray
        Complexity values
    Pi_x : np.ndarray
        Actual prime counts
    optimize : bool, default=True
        If True, fit α to minimize error. If False, use default α=0.1
        
    Returns
    -------
    B_x : np.ndarray
        Baseline values
    params : dict
        Fitted parameters and metrics
    """
    if optimize and len(x_values) > 1:
        # Fit α to minimize sum of squared errors
        # B(x) = αx, so we fit Pi_x ≈ αx
        valid_mask = x_values > 0
        if np.sum(valid_mask) > 0:
            x_valid = x_values[valid_mask]
            Pi_valid = Pi_x[valid_mask]
            # Linear regression: Pi = αx
            alpha = np.sum(Pi_valid * x_valid) / np.sum(x_valid ** 2)
            alpha = max(0.01, alpha)  # Ensure positive
        else:
            alpha = 0.1
    else:
        alpha = 0.1
    
    B_x = alpha * x_values
    B_x = np.maximum(B_x, 0)  # Ensure non-negative
    
    # Compute fit metrics
    residuals = Pi_x - B_x
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((Pi_x - np.mean(Pi_x)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    n = len(x_values)
    k = 1  # One parameter (alpha)
    aic = n * np.log(ss_res / n) + 2 * k if ss_res > 0 else np.inf
    bic = n * np.log(ss_res / n) + k * np.log(n) if ss_res > 0 else np.inf
    
    params = {
        'type': 'linear',
        'alpha': alpha,
        'r_squared': r_squared,
        'aic': aic,
        'bic': bic,
        'rmse': np.sqrt(ss_res / n) if n > 0 else 0.0
    }
    
    return B_x, params


def compute_prime_theorem_baseline(
    x_values: np.ndarray,
    Pi_x: np.ndarray,
    optimize: bool = True
) -> Tuple[np.ndarray, Dict]:
    """
    Compute Prime Theorem baseline B(x) = βx/log(x).
    
    Parameters
    ----------
    x_values : np.ndarray
        Complexity values
    Pi_x : np.ndarray
        Actual prime counts
    optimize : bool, default=True
        If True, fit β to minimize error
        
    Returns
    -------
    B_x : np.ndarray
        Baseline values
    params : dict
        Fitted parameters and metrics
    """
    # Avoid log(1) = 0
    valid_mask = x_values > 1
    if not np.any(valid_mask):
        B_x = np.zeros_like(x_values)
        params = {
            'type': 'prime_theorem',
            'beta': 1.0,
            'r_squared': 0.0,
            'aic': np.inf,
            'bic': np.inf,
            'rmse': 0.0
        }
        return B_x, params
    
    x_valid = x_values[valid_mask]
    Pi_valid = Pi_x[valid_mask]
    
    if optimize and len(x_valid) > 1:
        # Fit β: Pi ≈ βx/log(x)
        # β = Pi * log(x) / x
        log_x = np.log(x_valid)
        beta_estimates = (Pi_valid * log_x) / x_valid
        beta = np.median(beta_estimates[beta_estimates > 0])
        beta = max(0.01, beta)  # Ensure positive
    else:
        beta = 1.0
    
    B_x = np.zeros_like(x_values, dtype=float)
    for i, x in enumerate(x_values):
        if x > 1:
            B_x[i] = beta * x / np.log(x)
        else:
            B_x[i] = 0
    
    # Compute fit metrics (only on valid points)
    residuals = Pi_valid - B_x[valid_mask]
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((Pi_valid - np.mean(Pi_valid)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    n = len(x_valid)
    k = 1  # One parameter (beta)
    aic = n * np.log(ss_res / n) + 2 * k if ss_res > 0 and n > 0 else np.inf
    bic = n * np.log(ss_res / n) + k * np.log(n) if ss_res > 0 and n > 0 else np.inf
    
    params = {
        'type': 'prime_theorem',
        'beta': beta,
        'r_squared': r_squared,
        'aic': aic,
        'bic': bic,
        'rmse': np.sqrt(ss_res / n) if n > 0 else 0.0
    }
    
    return B_x, params


def compute_logarithmic_integral_baseline(
    x_values: np.ndarray,
    Pi_x: np.ndarray,
    optimize: bool = True
) -> Tuple[np.ndarray, Dict]:
    """
    Compute Logarithmic Integral baseline B(x) = β * Li(x).
    
    Li(x) = ∫₂ˣ dt/log(t) is the standard form in number theory.
    
    Parameters
    ----------
    x_values : np.ndarray
        Complexity values
    Pi_x : np.ndarray
        Actual prime counts
    optimize : bool, default=True
        If True, fit scaling factor β
        
    Returns
    -------
    B_x : np.ndarray
        Baseline values
    params : dict
        Fitted parameters and metrics
    """
    # Compute Li(x) for each x
    Li_x = np.array([logarithmic_integral(float(x)) for x in x_values])
    
    # Fit scaling factor β
    valid_mask = (Li_x > 0) & (x_values > 2)
    if optimize and np.sum(valid_mask) > 1:
        Li_valid = Li_x[valid_mask]
        Pi_valid = Pi_x[valid_mask]
        # Fit β: Pi ≈ β * Li
        beta = np.sum(Pi_valid * Li_valid) / np.sum(Li_valid ** 2)
        beta = max(0.01, beta)
    else:
        beta = 1.0
    
    B_x = beta * Li_x
    
    # Compute fit metrics
    valid_mask = Li_x > 0
    if np.sum(valid_mask) > 1:
        residuals = Pi_x[valid_mask] - B_x[valid_mask]
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((Pi_x[valid_mask] - np.mean(Pi_x[valid_mask])) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        n = np.sum(valid_mask)
    else:
        r_squared = 0.0
        ss_res = np.sum((Pi_x - B_x) ** 2)
        n = len(x_values)
    
    k = 1  # One parameter (beta)
    aic = n * np.log(ss_res / n) + 2 * k if ss_res > 0 and n > 0 else np.inf
    bic = n * np.log(ss_res / n) + k * np.log(n) if ss_res > 0 and n > 0 else np.inf
    
    params = {
        'type': 'logarithmic_integral',
        'beta': beta,
        'r_squared': r_squared,
        'aic': aic,
        'bic': bic,
        'rmse': np.sqrt(ss_res / n) if n > 0 else 0.0
    }
    
    return B_x, params


def compute_power_law_baseline(
    x_values: np.ndarray,
    Pi_x: np.ndarray,
    optimize: bool = True
) -> Tuple[np.ndarray, Dict]:
    """
    Compute power law baseline B(x) = γx^δ.
    
    Parameters
    ----------
    x_values : np.ndarray
        Complexity values
    Pi_x : np.ndarray
        Actual prime counts
    optimize : bool, default=True
        If True, fit γ and δ
        
    Returns
    -------
    B_x : np.ndarray
        Baseline values
    params : dict
        Fitted parameters and metrics
    """
    valid_mask = (x_values > 0) & (Pi_x >= 0)
    if not np.any(valid_mask) or np.sum(valid_mask) < 2:
        B_x = np.zeros_like(x_values)
        params = {
            'type': 'power_law',
            'gamma': 0.1,
            'delta': 1.0,
            'r_squared': 0.0,
            'aic': np.inf,
            'bic': np.inf,
            'rmse': 0.0
        }
        return B_x, params
    
    x_valid = x_values[valid_mask]
    Pi_valid = Pi_x[valid_mask]
    
    if optimize and len(x_valid) > 2:
        # Fit power law: Pi ≈ γx^δ
        # Take log: log(Pi) ≈ log(γ) + δ*log(x)
        # Linear regression in log space
        log_x = np.log(x_valid[x_valid > 0])
        log_Pi = np.log(np.maximum(Pi_valid[x_valid > 0], 0.01))  # Avoid log(0)
        
        if len(log_x) > 1:
            # Linear fit: log_Pi = a + b*log_x
            coeffs = np.polyfit(log_x, log_Pi, 1)
            delta = coeffs[0]
            log_gamma = coeffs[1]
            gamma = np.exp(log_gamma)
            gamma = max(0.01, gamma)
            delta = max(0.1, min(2.0, delta))  # Reasonable bounds
        else:
            gamma, delta = 0.1, 1.0
    else:
        gamma, delta = 0.1, 1.0
    
    B_x = gamma * (x_values ** delta)
    B_x = np.maximum(B_x, 0)
    
    # Compute fit metrics
    residuals = Pi_valid - B_x[valid_mask]
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((Pi_valid - np.mean(Pi_valid)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    n = len(x_valid)
    k = 2  # Two parameters (gamma, delta)
    aic = n * np.log(ss_res / n) + 2 * k if ss_res > 0 and n > 0 else np.inf
    bic = n * np.log(ss_res / n) + k * np.log(n) if ss_res > 0 and n > 0 else np.inf
    
    params = {
        'type': 'power_law',
        'gamma': gamma,
        'delta': delta,
        'r_squared': r_squared,
        'aic': aic,
        'bic': bic,
        'rmse': np.sqrt(ss_res / n) if n > 0 else 0.0
    }
    
    return B_x, params


def compare_all_baselines(
    x_values: np.ndarray,
    Pi_x: np.ndarray,
    optimize_params: bool = True
) -> Dict[str, Tuple[np.ndarray, Dict]]:
    """
    Compare all baseline functions and return their fits.
    
    Parameters
    ----------
    x_values : np.ndarray
        Complexity values
    Pi_x : np.ndarray
        Actual prime counts
    optimize_params : bool, default=True
        Whether to optimize parameters for each baseline
        
    Returns
    -------
    dict
        Dictionary mapping baseline type to (B_x, params) tuple
    """
    results = {}
    
    # Linear
    B_linear, params_linear = compute_linear_baseline(x_values, Pi_x, optimize_params)
    results['linear'] = (B_linear, params_linear)
    
    # Prime Theorem
    B_prime, params_prime = compute_prime_theorem_baseline(x_values, Pi_x, optimize_params)
    results['prime_theorem'] = (B_prime, params_prime)
    
    # Logarithmic Integral
    B_li, params_li = compute_logarithmic_integral_baseline(x_values, Pi_x, optimize_params)
    results['logarithmic_integral'] = (B_li, params_li)
    
    # Power Law
    B_power, params_power = compute_power_law_baseline(x_values, Pi_x, optimize_params)
    results['power_law'] = (B_power, params_power)
    
    return results


def select_best_baseline(
    comparison_results: Dict[str, Tuple[np.ndarray, Dict]],
    criterion: Literal['r_squared', 'aic', 'bic', 'rmse'] = 'aic'
) -> Tuple[str, np.ndarray, Dict]:
    """
    Select the best baseline function based on a criterion.
    
    Parameters
    ----------
    comparison_results : dict
        Results from compare_all_baselines()
    criterion : {'r_squared', 'aic', 'bic', 'rmse'}, default='aic'
        Selection criterion:
        - 'r_squared': Maximize R²
        - 'aic': Minimize AIC (Akaike Information Criterion)
        - 'bic': Minimize BIC (Bayesian Information Criterion)
        - 'rmse': Minimize RMSE
        
    Returns
    -------
    best_type : str
        Type of best baseline
    best_B_x : np.ndarray
        Best baseline values
    best_params : dict
        Parameters of best baseline
    """
    if not comparison_results:
        raise ValueError("No comparison results provided")
    
    if criterion == 'r_squared':
        # Maximize R²
        best_type = max(comparison_results.keys(), 
                       key=lambda k: comparison_results[k][1].get('r_squared', -np.inf))
    elif criterion in ['aic', 'bic', 'rmse']:
        # Minimize AIC, BIC, or RMSE
        best_type = min(comparison_results.keys(),
                       key=lambda k: comparison_results[k][1].get(criterion, np.inf))
    else:
        raise ValueError(f"Unknown criterion: {criterion}")
    
    best_B_x, best_params = comparison_results[best_type]
    
    return best_type, best_B_x, best_params


def generate_baseline_comparison_report(
    comparison_results: Dict[str, Tuple[np.ndarray, Dict]],
    x_values: np.ndarray,
    Pi_x: np.ndarray
) -> str:
    """
    Generate a text report comparing all baseline functions.
    
    Parameters
    ----------
    comparison_results : dict
        Results from compare_all_baselines()
    x_values : np.ndarray
        Complexity values
    Pi_x : np.ndarray
        Actual prime counts
        
    Returns
    -------
    str
        Formatted comparison report
    """
    lines = []
    lines.append("=" * 80)
    lines.append("BASELINE FUNCTION COMPARISON REPORT")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Number of data points: {len(x_values)}")
    lines.append(f"Complexity range: [{x_values[0]:.1f}, {x_values[-1]:.1f}]")
    lines.append(f"Total primes: {Pi_x[-1]:.0f}")
    lines.append("")
    lines.append("-" * 80)
    lines.append(f"{'Baseline Type':<25} {'R²':>8} {'AIC':>10} {'BIC':>10} {'RMSE':>10}")
    lines.append("-" * 80)
    
    for baseline_type, (B_x, params) in sorted(comparison_results.items()):
        r2 = params.get('r_squared', 0.0)
        aic = params.get('aic', np.inf)
        bic = params.get('bic', np.inf)
        rmse = params.get('rmse', 0.0)
        
        lines.append(f"{baseline_type:<25} {r2:>8.4f} {aic:>10.2f} {bic:>10.2f} {rmse:>10.4f}")
    
    lines.append("-" * 80)
    
    # Find best by each criterion
    best_r2 = select_best_baseline(comparison_results, 'r_squared')[0]
    best_aic = select_best_baseline(comparison_results, 'aic')[0]
    best_bic = select_best_baseline(comparison_results, 'bic')[0]
    best_rmse = select_best_baseline(comparison_results, 'rmse')[0]
    
    lines.append("")
    lines.append("Best Baseline by Criterion (main text focuses on AIC/BIC/RMSE; R² is diagnostic only):")
    lines.append(f"  R² (diagnostic): {best_r2}")
    lines.append(f"  AIC:             {best_aic}")
    lines.append(f"  BIC:             {best_bic}")
    lines.append(f"  RMSE:            {best_rmse}")
    lines.append("")
    lines.append(
        "Note: R² is computed in the usual way and may take large negative values when a baseline "
        "family is severely misspecified. In such cases, the model performs worse than a constant-"
        "mean reference; therefore, we rely primarily on AIC, BIC, and RMSE when comparing baselines "
        "in the main text, and treat R² as a supplementary fit-quality diagnostic."
    )
    lines.append("")
    lines.append("=" * 80)
    
    return "\n".join(lines)

