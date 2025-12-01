"""
Temporal Analysis Module

This module provides tools for analyzing temporal trends in ERH error evolution,
detecting anomalies (Mule effects), and forecasting future error growth.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from scipy import stats
from scipy.optimize import curve_fit
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def analyze_temporal_trends(
    E_xt: np.ndarray,
    time_steps: int,
    x_values: np.ndarray,
    complexity_subset: Optional[List[int]] = None
) -> Dict:
    """
    Analyze temporal trends in error evolution.
    
    Parameters
    ----------
    E_xt : np.ndarray
        2D error array of shape (time_steps, X_max)
    time_steps : int
        Number of time steps
    x_values : np.ndarray
        Array of complexity values
    complexity_subset : Optional[List[int]], default=None
        Specific complexity levels to analyze. If None, analyzes all.
        
    Returns
    -------
    Dict
        Analysis results containing:
        - 'trends_by_complexity': Dict mapping complexity to trend info
        - 'overall_trend': Overall trend across all complexities
        - 'volatility': Measure of temporal volatility
        - 'mean_error': Mean error over time
        - 'max_error': Maximum error over time
        
    Examples
    --------
    >>> E_xt = compute_E_temporal(Pi_xt, B_xt, time_steps=10, X_max=100)
    >>> x_vals = np.arange(1, 101)
    >>> trends = analyze_temporal_trends(E_xt, time_steps=10, x_values=x_vals)
    >>> print(f"Overall trend: {trends['overall_trend']}")
    """
    if complexity_subset is None:
        complexity_subset = x_values.tolist()
    
    trends_by_complexity = {}
    
    # Analyze each complexity level
    for x in complexity_subset:
        x_idx = int(x) - 1  # Convert to 0-indexed
        if 0 <= x_idx < E_xt.shape[1]:
            E_t = E_xt[:, x_idx]
            
            # Linear trend
            time_vals = np.arange(time_steps)
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_vals, E_t)
            
            # Volatility (standard deviation)
            volatility = np.std(E_t)
            
            # Mean and max
            mean_error = np.mean(E_t)
            max_error = np.max(np.abs(E_t))
            
            trends_by_complexity[x] = {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'volatility': volatility,
                'mean_error': mean_error,
                'max_error': max_error,
                'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
            }
    
    # Overall trend (average across all complexities)
    all_slopes = [info['slope'] for info in trends_by_complexity.values()]
    overall_slope = np.mean(all_slopes) if all_slopes else 0.0
    
    # Overall volatility
    all_volatilities = [info['volatility'] for info in trends_by_complexity.values()]
    overall_volatility = np.mean(all_volatilities) if all_volatilities else 0.0
    
    # Mean and max across all time and complexity
    overall_mean = np.mean(np.abs(E_xt))
    overall_max = np.max(np.abs(E_xt))
    
    return {
        'trends_by_complexity': trends_by_complexity,
        'overall_trend': {
            'slope': overall_slope,
            'direction': 'increasing' if overall_slope > 0.01 else 'decreasing' if overall_slope < -0.01 else 'stable',
            'volatility': overall_volatility,
            'mean_error': overall_mean,
            'max_error': overall_max
        },
        'volatility': overall_volatility,
        'mean_error': overall_mean,
        'max_error': overall_max
    }


def detect_anomalies(
    E_xt: np.ndarray,
    threshold: Optional[float] = None,
    method: str = 'statistical',
    C: float = 1.0,
    epsilon: float = 0.1,
    X_max: int = 100
) -> List[Dict]:
    """
    Detect anomalies in temporal error evolution.
    
    Anomalies correspond to "Mule" events in psychohistory - sudden disruptions
    that violate expected patterns.
    
    Parameters
    ----------
    E_xt : np.ndarray
        2D error array of shape (time_steps, X_max)
    threshold : Optional[float], default=None
        Custom threshold for anomaly detection. If None, uses ERH bound or statistical method
    method : str, default='statistical'
        Detection method:
        - 'statistical': Use z-score (outliers beyond 3 standard deviations)
        - 'erh_bound': Use ERH theoretical bound
        - 'combined': Use both methods
    C : float, default=1.0
        ERH constant (for 'erh_bound' method)
    epsilon : float, default=0.1
        ERH epsilon parameter (for 'erh_bound' method)
    X_max : int, default=100
        Maximum complexity
        
    Returns
    -------
    List[Dict]
        List of detected anomalies, each containing:
        - 'time': time step
        - 'complexity': complexity level
        - 'error_value': E(x,t) value
        - 'error_magnitude': |E(x,t)|
        - 'z_score': z-score (if statistical method used)
        - 'erh_violation': whether it violates ERH bound
        - 'severity': severity level ('low', 'medium', 'high', 'critical')
        
    Examples
    --------
    >>> E_xt = compute_E_temporal(Pi_xt, B_xt, time_steps=10, X_max=100)
    >>> anomalies = detect_anomalies(E_xt, method='combined')
    >>> print(f"Detected {len(anomalies)} anomalies")
    """
    anomalies = []
    time_steps = E_xt.shape[0]
    x_values = np.arange(1, X_max + 1)
    
    # Statistical method: compute z-scores
    if method in ['statistical', 'combined']:
        error_magnitudes = np.abs(E_xt)
        mean_error = np.mean(error_magnitudes)
        std_error = np.std(error_magnitudes)
        
        # Z-scores
        z_scores = (error_magnitudes - mean_error) / (std_error + 1e-10)
        z_threshold = 3.0  # 3 standard deviations
    
    # ERH bound method
    if method in ['erh_bound', 'combined']:
        erh_bounds = C * (x_values ** (0.5 + epsilon))
    
    for t in range(time_steps):
        for x_idx, x in enumerate(x_values):
            error_value = E_xt[t, x_idx]
            error_mag = abs(error_value)
            
            is_anomaly = False
            z_score = None
            erh_violation = False
            severity = 'low'
            
            # Check statistical anomaly
            if method in ['statistical', 'combined']:
                z_score = z_scores[t, x_idx]
                if abs(z_score) > z_threshold:
                    is_anomaly = True
                    if abs(z_score) > 5:
                        severity = 'critical'
                    elif abs(z_score) > 4:
                        severity = 'high'
                    elif abs(z_score) > 3:
                        severity = 'medium'
            
            # Check ERH violation
            violation_ratio = None
            if method in ['erh_bound', 'combined']:
                erh_bound = erh_bounds[x_idx]
                violation_ratio = error_mag / (erh_bound + 1e-10)  # Avoid division by zero
                if error_mag > erh_bound * 1.5:  # 50% above bound
                    erh_violation = True
                    if not is_anomaly:
                        is_anomaly = True
                    if error_mag > erh_bound * 3:
                        severity = 'critical'
                    elif error_mag > erh_bound * 2:
                        severity = 'high'
                    elif error_mag > erh_bound * 1.5:
                        severity = 'medium'
            
            # Custom threshold
            if threshold is not None and error_mag > threshold:
                is_anomaly = True
                if error_mag > threshold * 2:
                    severity = 'critical'
                elif error_mag > threshold * 1.5:
                    severity = 'high'
            
            if is_anomaly:
                anomaly_dict = {
                    'time': t,
                    'complexity': x,
                    'error_value': error_value,
                    'error_magnitude': error_mag,
                    'z_score': z_score,
                    'erh_violation': erh_violation,
                    'severity': severity
                }
                if violation_ratio is not None:
                    anomaly_dict['violation_ratio'] = violation_ratio
                anomalies.append(anomaly_dict)
    
    # Sort by severity and magnitude
    severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
    anomalies.sort(key=lambda a: (severity_order.get(a['severity'], 0), a['error_magnitude']), reverse=True)
    
    return anomalies


def forecast_error_growth(
    E_xt: np.ndarray,
    forecast_horizon: int = 5,
    method: str = 'linear',
    complexity_subset: Optional[List[int]] = None,
    X_max: int = 100
) -> Dict:
    """
    Forecast future error growth based on historical data.
    
    Parameters
    ----------
    E_xt : np.ndarray
        2D error array of shape (time_steps, X_max)
    forecast_horizon : int, default=5
        Number of future time steps to forecast
    method : str, default='linear'
        Forecasting method:
        - 'linear': Linear extrapolation
        - 'polynomial': Polynomial fitting
        - 'exponential': Exponential smoothing
        - 'ar': Auto-regressive model (if sklearn available)
    complexity_subset : Optional[List[int]], default=None
        Specific complexity levels to forecast. If None, forecasts all.
    X_max : int, default=100
        Maximum complexity
        
    Returns
    -------
    Dict
        Forecast results containing:
        - 'forecast': 2D array of shape (forecast_horizon, X_max) with predicted errors
        - 'confidence_intervals': Confidence intervals for forecasts
        - 'forecast_errors': Forecast error metrics
        - 'method_used': Method actually used
        
    Examples
    --------
    >>> E_xt = compute_E_temporal(Pi_xt, B_xt, time_steps=10, X_max=100)
    >>> forecast = forecast_error_growth(E_xt, forecast_horizon=5, method='linear')
    >>> future_errors = forecast['forecast']
    """
    time_steps = E_xt.shape[0]
    x_values = np.arange(1, X_max + 1)
    
    if complexity_subset is None:
        complexity_subset = x_values.tolist()
    
    forecast_array = np.zeros((forecast_horizon, X_max))
    confidence_lower = np.zeros((forecast_horizon, X_max))
    confidence_upper = np.zeros((forecast_horizon, X_max))
    
    time_vals = np.arange(time_steps)
    future_times = np.arange(time_steps, time_steps + forecast_horizon)
    
    for x in complexity_subset:
        x_idx = int(x) - 1
        if 0 <= x_idx < E_xt.shape[1]:
            E_t = E_xt[:, x_idx]
            
            if method == 'linear':
                # Linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(time_vals, E_t)
                
                # Forecast
                forecast_values = intercept + slope * future_times
                forecast_array[:, x_idx] = forecast_values
                
                # Confidence intervals (simplified)
                se = std_err * np.sqrt(1 + 1/time_steps + (future_times - np.mean(time_vals))**2 / np.sum((time_vals - np.mean(time_vals))**2))
                t_critical = stats.t.ppf(0.95, time_steps - 2)
                confidence_lower[:, x_idx] = forecast_values - t_critical * se
                confidence_upper[:, x_idx] = forecast_values + t_critical * se
                
            elif method == 'polynomial' and SKLEARN_AVAILABLE:
                # Polynomial regression
                poly_features = PolynomialFeatures(degree=2)
                X_poly = poly_features.fit_transform(time_vals.reshape(-1, 1))
                model = LinearRegression()
                model.fit(X_poly, E_t)
                
                # Forecast
                X_future_poly = poly_features.transform(future_times.reshape(-1, 1))
                forecast_values = model.predict(X_future_poly)
                forecast_array[:, x_idx] = forecast_values
                
                # Simple confidence intervals
                residuals = E_t - model.predict(X_poly)
                std_residual = np.std(residuals)
                confidence_lower[:, x_idx] = forecast_values - 1.96 * std_residual
                confidence_upper[:, x_idx] = forecast_values + 1.96 * std_residual
                
            elif method == 'exponential':
                # Exponential smoothing (simple)
                alpha = 0.3  # smoothing parameter
                last_value = E_t[-1]
                trend = E_t[-1] - E_t[-2] if len(E_t) > 1 else 0
                
                forecast_values = []
                for h in range(forecast_horizon):
                    forecast_val = last_value + trend * (h + 1)
                    forecast_values.append(forecast_val)
                
                forecast_array[:, x_idx] = forecast_values
                
                # Simple confidence intervals
                std_residual = np.std(np.diff(E_t))
                confidence_lower[:, x_idx] = forecast_values - 1.96 * std_residual
                confidence_upper[:, x_idx] = forecast_values + 1.96 * std_residual
                
            else:
                # Fallback to linear
                slope, intercept, _, _, std_err = stats.linregress(time_vals, E_t)
                forecast_values = intercept + slope * future_times
                forecast_array[:, x_idx] = forecast_values
                se = std_err * np.sqrt(1 + 1/time_steps)
                confidence_lower[:, x_idx] = forecast_values - 1.96 * se
                confidence_upper[:, x_idx] = forecast_values + 1.96 * se
                method = 'linear'  # Update method used
    
    # Compute forecast errors (if we had validation data)
    forecast_errors = {
        'method': method,
        'forecast_horizon': forecast_horizon,
        'mean_forecast': np.mean(np.abs(forecast_array)),
        'max_forecast': np.max(np.abs(forecast_array))
    }
    
    return {
        'forecast': forecast_array,
        'confidence_intervals': {
            'lower': confidence_lower,
            'upper': confidence_upper
        },
        'forecast_errors': forecast_errors,
        'method_used': method,
        'forecast_times': future_times
    }


def compute_temporal_erh_satisfaction(
    E_xt: np.ndarray,
    C: float = 1.0,
    epsilon: float = 0.1,
    X_max: int = 100
) -> Dict:
    """
    Check if temporal error evolution satisfies ERH bounds over time.
    
    Parameters
    ----------
    E_xt : np.ndarray
        2D error array
    C : float, default=1.0
        ERH constant
    epsilon : float, default=0.1
        ERH epsilon parameter
    X_max : int, default=100
        Maximum complexity
        
    Returns
    -------
    Dict
        ERH satisfaction metrics:
        - 'satisfied': boolean array of shape (time_steps, X_max)
        - 'violation_count': number of violations
        - 'violation_rate': fraction of violations
        - 'worst_violation': maximum violation ratio
        - 'time_steps_satisfied': number of time steps that fully satisfy ERH
    """
    time_steps = E_xt.shape[0]
    x_values = np.arange(1, X_max + 1)
    
    # Compute ERH bounds
    erh_bounds = C * (x_values ** (0.5 + epsilon))
    
    # Check satisfaction
    error_magnitudes = np.abs(E_xt)
    satisfied = error_magnitudes <= erh_bounds[np.newaxis, :]
    
    violation_count = np.sum(~satisfied)
    total_points = time_steps * X_max
    violation_rate = violation_count / total_points if total_points > 0 else 0.0
    
    # Worst violation
    violation_ratios = error_magnitudes / (erh_bounds[np.newaxis, :] + 1e-10)
    worst_violation = np.max(violation_ratios)
    
    # Time steps fully satisfied
    time_steps_satisfied = np.sum(np.all(satisfied, axis=1))
    
    return {
        'satisfied': satisfied,
        'violation_count': violation_count,
        'violation_rate': violation_rate,
        'worst_violation': worst_violation,
        'time_steps_satisfied': time_steps_satisfied,
        'time_steps_total': time_steps,
        'satisfaction_rate': time_steps_satisfied / time_steps if time_steps > 0 else 0.0
    }
