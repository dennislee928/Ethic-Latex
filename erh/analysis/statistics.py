"""
Statistics Module

Provides statistical analysis tools for comparing judges, fitting error growth,
and generating reports.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import json


def fit_error_growth(
    E_x: np.ndarray,
    x_values: np.ndarray,
    model: str = 'power_law'
) -> dict:
    """
    Fit a model to the error growth |E(x)|.
    
    Parameters
    ----------
    E_x : np.ndarray
        Error values
    x_values : np.ndarray
        Complexity values
    model : str, default='power_law'
        Model type: 'power_law', 'linear', 'quadratic', 'logarithmic'
        
    Returns
    -------
    dict
        Fitted parameters and goodness of fit metrics
        
    Examples
    --------
    >>> fit_result = fit_error_growth(E_x, x_vals, model='power_law')
    >>> print(f"Exponent: {fit_result['exponent']:.3f}")
    >>> print(f"R²: {fit_result['r_squared']:.3f}")
    """
    abs_E = np.abs(E_x)
    valid_mask = (abs_E > 0) & (x_values > 1)
    
    if np.sum(valid_mask) < 3:
        return {'error': 'insufficient_data'}
    
    x = x_values[valid_mask]
    y = abs_E[valid_mask]
    
    result = {}
    
    try:
        if model == 'power_law':
            # Fit |E(x)| = C * x^α
            def power_law(x, C, alpha):
                return C * (x ** alpha)
            
            # Initial guess
            p0 = [1.0, 0.5]
            params, _ = curve_fit(power_law, x, y, p0=p0, maxfev=5000)
            C, alpha = params
            
            y_pred = power_law(x, C, alpha)
            
            result['model'] = 'power_law'
            result['constant'] = C
            result['exponent'] = alpha
            result['formula'] = f'{C:.3f} * x^{alpha:.3f}'
            
        elif model == 'linear':
            # Fit |E(x)| = a * x + b
            coeffs = np.polyfit(x, y, 1)
            y_pred = np.polyval(coeffs, x)
            
            result['model'] = 'linear'
            result['slope'] = coeffs[0]
            result['intercept'] = coeffs[1]
            result['formula'] = f'{coeffs[0]:.3f} * x + {coeffs[1]:.3f}'
            
        elif model == 'quadratic':
            # Fit |E(x)| = a * x^2 + b * x + c
            coeffs = np.polyfit(x, y, 2)
            y_pred = np.polyval(coeffs, x)
            
            result['model'] = 'quadratic'
            result['coefficients'] = coeffs.tolist()
            result['formula'] = f'{coeffs[0]:.3e} * x^2 + {coeffs[1]:.3f} * x + {coeffs[2]:.3f}'
            
        elif model == 'logarithmic':
            # Fit |E(x)| = a * log(x) + b
            log_x = np.log(x)
            coeffs = np.polyfit(log_x, y, 1)
            y_pred = np.polyval(coeffs, log_x)
            
            result['model'] = 'logarithmic'
            result['coefficient'] = coeffs[0]
            result['constant'] = coeffs[1]
            result['formula'] = f'{coeffs[0]:.3f} * log(x) + {coeffs[1]:.3f}'
        else:
            return {'error': f'unknown_model: {model}'}
        
        # Compute R²
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Compute RMSE
        rmse = np.sqrt(np.mean((y - y_pred) ** 2))
        
        result['r_squared'] = r_squared
        result['rmse'] = rmse
        result['num_points'] = len(x)
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def compare_judges(
    results_dict: Dict[str, List],
    X_max: int = 100,
    baseline: str = 'prime_theorem'
) -> dict:
    """
    Compare multiple judges across various metrics.
    
    Parameters
    ----------
    results_dict : Dict[str, List[Action]]
        Dictionary mapping judge names to lists of evaluated actions
    X_max : int, default=100
        Maximum complexity for analysis
    baseline : str, default='prime_theorem'
        Baseline type for error computation
        
    Returns
    -------
    dict
        Comprehensive comparison across judges
        
    Examples
    --------
    >>> judges = {'biased': BiasedJudge(), 'noisy': NoisyJudge()}
    >>> results = batch_evaluate(actions, judges)
    >>> comparison = compare_judges(results)
    >>> for name, metrics in comparison.items():
    ...     print(f"{name}: ERH satisfied = {metrics['erh_satisfied']}")
    """
    # Handle both relative and absolute imports
    try:
        from ..core.ethical_primes import (
            select_ethical_primes,
            compute_Pi_and_error,
            analyze_error_growth
        )
    except ImportError:
        # Fallback for direct script execution
        from core.ethical_primes import (
            select_ethical_primes,
            compute_Pi_and_error,
            analyze_error_growth
        )
    
    comparison = {}
    
    for name, actions in results_dict.items():
        # Select primes
        primes = select_ethical_primes(actions)
        
        if len(primes) == 0:
            comparison[name] = {
                'error': 'no_primes_found',
                'num_mistakes': sum(a.mistake_flag for a in actions if a.mistake_flag is not None)
            }
            continue
        
        # Compute error distribution
        Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=X_max, baseline=baseline)
        
        # Analyze error growth
        growth_analysis = analyze_error_growth(E_x, x_vals)
        
        # Compute judgment metrics
        deltas = [a.delta for a in actions if a.delta is not None]
        mistakes = [a.mistake_flag for a in actions if a.mistake_flag is not None]
        
        comparison[name] = {
            'num_actions': len(actions),
            'num_primes': len(primes),
            'prime_ratio': len(primes) / len(actions),
            'mistake_rate': np.mean(mistakes) if mistakes else 0,
            'mae': np.mean(np.abs(deltas)) if deltas else 0,
            'rmse': np.sqrt(np.mean(np.array(deltas)**2)) if deltas else 0,
            'max_error': np.max(np.abs(E_x)),
            'mean_error': np.mean(np.abs(E_x)),
            'estimated_exponent': growth_analysis['estimated_exponent'],
            'erh_satisfied': growth_analysis['erh_satisfied'],
            'growth_rate': growth_analysis['growth_rate'],
            'r_squared': growth_analysis['r_squared']
        }
    
    return comparison


def detect_structural_bias(
    actions: List,
    complexity_bins: int = 10
) -> dict:
    """
    Detect if there's structural bias correlated with complexity.
    
    Parameters
    ----------
    actions : List[Action]
        List of evaluated actions
    complexity_bins : int, default=10
        Number of bins to divide complexity range
        
    Returns
    -------
    dict
        Analysis of bias patterns including correlation and bin statistics
        
    Examples
    --------
    >>> actions = generate_world(1000)
    >>> judge = BiasedJudge(bias_strength=0.3)
    >>> evaluate_judgement(actions, judge)
    >>> bias_analysis = detect_structural_bias(actions)
    >>> print(f"Correlation: {bias_analysis['complexity_error_correlation']:.3f}")
    """
    # Extract data
    complexities = np.array([a.c for a in actions if a.delta is not None])
    errors = np.array([a.delta for a in actions if a.delta is not None])
    abs_errors = np.abs(errors)
    
    if len(complexities) < 10:
        return {'error': 'insufficient_data'}
    
    # Compute correlation between complexity and error magnitude
    corr, p_value = pearsonr(complexities, abs_errors)
    
    # Bin analysis
    bins = np.linspace(complexities.min(), complexities.max(), complexity_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    bin_mean_errors = []
    bin_std_errors = []
    bin_counts = []
    
    for i in range(complexity_bins):
        mask = (complexities >= bins[i]) & (complexities < bins[i+1])
        if i == complexity_bins - 1:
            mask = (complexities >= bins[i]) & (complexities <= bins[i+1])
        
        bin_errors = abs_errors[mask]
        if len(bin_errors) > 0:
            bin_mean_errors.append(np.mean(bin_errors))
            bin_std_errors.append(np.std(bin_errors))
            bin_counts.append(len(bin_errors))
        else:
            bin_mean_errors.append(0)
            bin_std_errors.append(0)
            bin_counts.append(0)
    
    # Check for monotonic trend
    is_increasing = all(bin_mean_errors[i] <= bin_mean_errors[i+1] 
                       for i in range(len(bin_mean_errors)-1) 
                       if bin_counts[i] > 0 and bin_counts[i+1] > 0)
    
    result = {
        'complexity_error_correlation': corr,
        'correlation_p_value': p_value,
        'correlation_significant': p_value < 0.05,
        'bins': {
            'centers': bin_centers.tolist(),
            'mean_errors': bin_mean_errors,
            'std_errors': bin_std_errors,
            'counts': bin_counts
        },
        'monotonic_increasing': is_increasing,
        'interpretation': ''
    }
    
    # Add interpretation
    if abs(corr) < 0.3:
        result['interpretation'] = "Weak or no correlation between complexity and error."
    elif corr > 0.3:
        result['interpretation'] = (
            f"Positive correlation ({corr:.2f}): errors increase with complexity. "
            "This suggests the judge struggles more with complex cases."
        )
    else:
        result['interpretation'] = (
            f"Negative correlation ({corr:.2f}): errors decrease with complexity. "
            "This is unusual and may indicate over-confidence on simple cases."
        )
    
    return result


def generate_report(
    results_dict: Dict[str, List],
    output_path: Optional[str] = None,
    format: str = 'markdown'
) -> str:
    """
    Generate a comprehensive report comparing judges.
    
    Parameters
    ----------
    results_dict : Dict[str, List[Action]]
        Dictionary mapping judge names to evaluated actions
    output_path : Optional[str], default=None
        If specified, save report to this file
    format : str, default='markdown'
        Output format: 'markdown', 'json', 'text'
        
    Returns
    -------
    str
        Report content
        
    Examples
    --------
    >>> report = generate_report(results, output_path='simulation/output/report.md')
    >>> print(report[:200])
    """
    comparison = compare_judges(results_dict)
    
    if format == 'json':
        report = json.dumps(comparison, indent=2, default=str)
        
    elif format == 'markdown':
        lines = ["# Ethical Riemann Hypothesis - Judge Comparison Report", ""]
        lines.append(f"**Number of judges analyzed:** {len(comparison)}")
        lines.append("")
        
        lines.append("## Summary Table")
        lines.append("")
        # Summary uses the canonical ERH decision from the centralized bound check.
        lines.append("| Judge | Actions | Primes | Mistake Rate | MAE | Exponent | ERH Satisfied | Growth Rate |")
        lines.append("|-------|---------|--------|--------------|-----|----------|---------------|-------------|")
        
        for name, metrics in comparison.items():
            if 'error' in metrics:
                lines.append(f"| {name} | - | - | - | - | - | ERROR | - |")
                continue
            
            lines.append(
                f"| {name} | {metrics['num_actions']} | {metrics['num_primes']} | "
                f"{metrics['mistake_rate']:.3f} | {metrics['mae']:.3f} | "
                f"{metrics['estimated_exponent']:.3f} | "
                f"{'Yes' if metrics.get('erh_satisfied', False) else 'No'} | "
                f"{metrics['growth_rate']} |"
            )
        
        lines.append("")
        lines.append("## Detailed Analysis")
        lines.append("")
        
        for name, metrics in comparison.items():
            lines.append(f"### {name}")
            lines.append("")
            
            if 'error' in metrics:
                lines.append(f"**Error:** {metrics['error']}")
                lines.append("")
                continue
            
            lines.append(f"- **Total Actions:** {metrics['num_actions']}")
            lines.append(f"- **Ethical Primes:** {metrics['num_primes']} ({metrics['prime_ratio']:.2%})")
            lines.append(f"- **Mistake Rate:** {metrics['mistake_rate']:.3f}")
            lines.append(f"- **Mean Absolute Error:** {metrics['mae']:.3f}")
            lines.append(f"- **RMSE:** {metrics['rmse']:.3f}")
            lines.append(f"- **Estimated Growth Exponent:** {metrics['estimated_exponent']:.3f}")
            # Canonical bound-based ERH decision
            lines.append(
                f"- **ERH Bound Satisfied (|E(x)| ≤ C·x^(1/2+ε) up to slack)?** "
                f"{'Yes' if metrics.get('erh_satisfied', False) else 'No'}"
            )
            lines.append(f"- **Growth Rate Category:** {metrics['growth_rate']}")
            lines.append(f"- **R² (fit quality):** {metrics['r_squared']:.3f}")
            lines.append("")
            
            # Interpretation – now keyed to bound satisfaction, with α as a side diagnostic.
            if metrics.get('erh_satisfied', False):
                lines.append(
                    "**Interpretation:** This judge's cumulative error stays within the ERH-style "
                    "bound (up to the allowed slack), indicating 'Riemann-healthy' behavior. "
                    "The exponent α is reported as an auxiliary diagnostic, not the primary test."
                )
            else:
                if metrics['growth_rate'] == 'superlinear':
                    lines.append(
                        "**Interpretation:** ⚠️ This judge shows problematic error growth. "
                        "Errors frequently exceed the ERH-style bound and grow faster than "
                        "linearly with complexity."
                    )
                elif metrics['growth_rate'] in ['linear', 'sublinear_fast']:
                    lines.append(
                        "**Interpretation:** This judge exhibits moderate error growth: the ERH-style "
                        "bound is not strictly satisfied, but errors do not explode catastrophically."
                    )
                else:
                    lines.append(
                        "**Interpretation:** Although the bound test flags some violations, the fitted "
                        "exponent α is below the √x target, suggesting a conservative or over-cautious "
                        "system whose long-run errors grow slower than the ERH worst case."
                    )
            
            lines.append("")
        
        report = "\n".join(lines)
        
    elif format == 'text':
        lines = ["Ethical Riemann Hypothesis - Judge Comparison Report"]
        lines.append("=" * 60)
        lines.append("")
        
        for name, metrics in comparison.items():
            lines.append(f"Judge: {name}")
            lines.append("-" * 60)
            
            if 'error' in metrics:
                lines.append(f"  Error: {metrics['error']}")
                lines.append("")
                continue
            
            for key, value in metrics.items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        report = "\n".join(lines)
    else:
        raise ValueError(f"Unknown format: {format}")
    
    # Save to file if requested
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    return report


def compute_judge_rankings(
    comparison: dict,
    metrics: List[str] = ['erh_satisfied', 'estimated_exponent', 'mae']
) -> dict:
    """
    Rank judges based on specified metrics.
    
    Parameters
    ----------
    comparison : dict
        Output from compare_judges
    metrics : List[str], default=['erh_satisfied', 'estimated_exponent', 'mae']
        Metrics to use for ranking
        
    Returns
    -------
    dict
        Rankings for each metric
    """
    rankings = {}
    
    for metric in metrics:
        values = []
        for name, data in comparison.items():
            if 'error' not in data and metric in data:
                values.append((name, data[metric]))
        
        if metric in ['mae', 'rmse', 'estimated_exponent']:
            # Lower is better
            values.sort(key=lambda x: x[1])
        elif metric == 'erh_satisfied':
            # True is better
            values.sort(key=lambda x: not x[1])
        else:
            values.sort(key=lambda x: x[1], reverse=True)
        
        rankings[metric] = [name for name, _ in values]
    
    return rankings


def bootstrap_exponent_ci(
    E_x: np.ndarray,
    x_values: np.ndarray,
    n_bootstrap: int = 500,
    ci: float = 0.95,
) -> Dict[str, float]:
    """
    Estimate uncertainty for the growth exponent α via bootstrap.

    We reuse the same log–log regression protocol as `fit_error_growth`,
    but repeatedly resample the (x, |E(x)|) pairs with replacement and
    refit α to obtain an empirical distribution.

    Parameters
    ----------
    E_x : np.ndarray
        Error values E(x).
    x_values : np.ndarray
        Corresponding complexity values x.
    n_bootstrap : int, default=500
        Number of bootstrap resamples.
    ci : float, default=0.95
        Confidence level for the interval.

    Returns
    -------
    dict
        - 'alpha_hat': point estimate from the full data
        - 'alpha_ci_low': lower confidence bound
        - 'alpha_ci_high': upper confidence bound
        - 'num_samples': number of valid points used
    """
    abs_E = np.abs(E_x)
    valid_mask = (abs_E > 0) & (x_values > 1)

    if np.sum(valid_mask) < 5:
        return {
            "alpha_hat": float("nan"),
            "alpha_ci_low": float("nan"),
            "alpha_ci_high": float("nan"),
            "num_samples": int(np.sum(valid_mask)),
        }

    x = x_values[valid_mask]
    y = abs_E[valid_mask]

    log_x = np.log(x)
    log_y = np.log(y)

    # Point estimate from full data
    coeffs = np.polyfit(log_x, log_y, 1)
    alpha_hat = float(coeffs[0])

    # Bootstrap distribution
    n = len(log_x)
    alphas = []
    rng = np.random.default_rng()

    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        bx = log_x[idx]
        by = log_y[idx]
        # Guard against degenerate resamples
        if np.std(bx) == 0 or np.std(by) == 0:
            continue
        bcoeffs = np.polyfit(bx, by, 1)
        alphas.append(bcoeffs[0])

    if not alphas:
        return {
            "alpha_hat": alpha_hat,
            "alpha_ci_low": float("nan"),
            "alpha_ci_high": float("nan"),
            "num_samples": n,
        }

    alphas_arr = np.asarray(alphas)
    lower = float(np.quantile(alphas_arr, (1 - ci) / 2))
    upper = float(np.quantile(alphas_arr, 1 - (1 - ci) / 2))

    return {
        "alpha_hat": alpha_hat,
        "alpha_ci_low": lower,
        "alpha_ci_high": upper,
        "num_samples": n,
    }

