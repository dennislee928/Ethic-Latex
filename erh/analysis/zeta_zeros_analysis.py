"""
Zeta Zeros Deep Analysis Module

This module provides advanced analysis of ethical zeta function zeros,
including critical line analysis, zero density, and correlation studies.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from scipy.optimize import minimize
from scipy.integrate import quad
import warnings


def refine_zero_newton_raphson(
    zeta_function: callable,
    initial_guess: complex,
    max_iterations: int = 20,
    tolerance: float = 1e-6
) -> Optional[complex]:
    """
    Refine zero location using Newton-Raphson method.
    
    Parameters
    ----------
    zeta_function : callable
        Function ζ_E(s) that returns complex value
    initial_guess : complex
        Initial guess for zero location
    max_iterations : int, default=20
        Maximum iterations
    tolerance : float, default=1e-6
        Convergence tolerance
        
    Returns
    -------
    complex or None
        Refined zero location, or None if convergence fails
    """
    s = initial_guess
    
    for _ in range(max_iterations):
        try:
            zeta_val = zeta_function(s)
            
            if abs(zeta_val) < tolerance:
                return s
            
            # Numerical derivative for Newton-Raphson
            h = 1e-8
            zeta_deriv = (zeta_function(s + h) - zeta_function(s - h)) / (2 * h)
            
            if abs(zeta_deriv) < 1e-10:
                break
            
            # Newton step
            s_new = s - zeta_val / zeta_deriv
            
            # Check for convergence
            if abs(s_new - s) < tolerance:
                return s_new
            
            s = s_new
            
        except (OverflowError, ZeroDivisionError, RuntimeWarning):
            break
    
    return None


def compute_zero_density(
    zeros: List[complex],
    real_range: Tuple[float, float],
    imag_range: Tuple[float, float]
) -> Dict:
    """
    Compute zero density statistics.
    
    Parameters
    ----------
    zeros : List[complex]
        List of zero locations
    real_range : Tuple[float, float]
        Range of Re(s)
    imag_range : Tuple[float, float]
        Range of Im(s)
        
    Returns
    -------
    dict
        Density statistics
    """
    if len(zeros) == 0:
        return {
            'total_zeros': 0,
            'area': 0.0,
            'density': 0.0,
            'zeros_per_unit_area': 0.0
        }
    
    area = (real_range[1] - real_range[0]) * (imag_range[1] - imag_range[0])
    
    return {
        'total_zeros': len(zeros),
        'area': area,
        'density': len(zeros) / area if area > 0 else 0.0,
        'zeros_per_unit_area': len(zeros) / area if area > 0 else 0.0
    }


def analyze_critical_line_proximity(
    zeros: List[complex],
    critical_line: float = 0.5
) -> Dict:
    """
    Analyze how close zeros are to the critical line Re(s) = 1/2.
    
    Parameters
    ----------
    zeros : List[complex]
        List of zero locations
    critical_line : float, default=0.5
        Critical line value (typically 0.5)
        
    Returns
    -------
    dict
        Critical line analysis results
    """
    if len(zeros) == 0:
        return {
            'mean_distance': np.nan,
            'median_distance': np.nan,
            'min_distance': np.nan,
            'max_distance': np.nan,
            'within_0.1': 0,
            'within_0.05': 0,
            'within_0.01': 0
        }
    
    distances = [abs(z.real - critical_line) for z in zeros]
    
    return {
        'mean_distance': np.mean(distances),
        'median_distance': np.median(distances),
        'min_distance': np.min(distances),
        'max_distance': np.max(distances),
        'std_distance': np.std(distances),
        'within_0.1': sum(1 for d in distances if d < 0.1),
        'within_0.05': sum(1 for d in distances if d < 0.05),
        'within_0.01': sum(1 for d in distances if d < 0.01),
        'fraction_within_0.1': sum(1 for d in distances if d < 0.1) / len(zeros),
        'fraction_within_0.05': sum(1 for d in distances if d < 0.05) / len(zeros),
        'fraction_within_0.01': sum(1 for d in distances if d < 0.01) / len(zeros)
    }


def compute_pair_correlation(
    zeros: List[complex],
    max_distance: float = 5.0,
    num_bins: int = 50
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute pair correlation function for zeros.
    
    This measures the distribution of distances between zero pairs,
    analogous to studies of Riemann zeta zeros.
    
    Parameters
    ----------
    zeros : List[complex]
        List of zero locations
    max_distance : float, default=5.0
        Maximum distance to consider
    num_bins : int, default=50
        Number of bins for histogram
        
    Returns
    -------
    distances : np.ndarray
        Distance values (bin centers)
    correlation : np.ndarray
        Pair correlation values
    """
    if len(zeros) < 2:
        return np.array([]), np.array([])
    
    # Compute all pairwise distances
    pair_distances = []
    for i in range(len(zeros)):
        for j in range(i + 1, len(zeros)):
            dist = abs(zeros[i] - zeros[j])
            if dist <= max_distance:
                pair_distances.append(dist)
    
    if len(pair_distances) == 0:
        return np.array([]), np.array([])
    
    # Histogram
    hist, bin_edges = np.histogram(pair_distances, bins=num_bins, range=(0, max_distance))
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    
    # Normalize by expected density (for uniform distribution)
    expected_density = len(pair_distances) / max_distance
    correlation = hist / (expected_density * (bin_edges[1] - bin_edges[0]) * len(zeros))
    
    return bin_centers, correlation


def compute_spacing_distribution(
    zeros: List[complex],
    sort_by: str = 'imaginary'
) -> Dict:
    """
    Compute spacing distribution between consecutive zeros.
    
    Parameters
    ----------
    zeros : List[complex]
        List of zero locations
    sort_by : {'imaginary', 'real', 'magnitude'}, default='imaginary'
        How to sort zeros before computing spacings
        
    Returns
    -------
    dict
        Spacing statistics
    """
    if len(zeros) < 2:
        return {
            'mean_spacing': np.nan,
            'median_spacing': np.nan,
            'std_spacing': np.nan,
            'spacings': []
        }
    
    # Sort zeros
    if sort_by == 'imaginary':
        sorted_zeros = sorted(zeros, key=lambda z: z.imag)
    elif sort_by == 'real':
        sorted_zeros = sorted(zeros, key=lambda z: z.real)
    else:  # magnitude
        sorted_zeros = sorted(zeros, key=lambda z: abs(z))
    
    # Compute spacings
    spacings = []
    for i in range(len(sorted_zeros) - 1):
        spacing = abs(sorted_zeros[i + 1] - sorted_zeros[i])
        spacings.append(spacing)
    
    if len(spacings) == 0:
        return {
            'mean_spacing': np.nan,
            'median_spacing': np.nan,
            'std_spacing': np.nan,
            'spacings': []
        }
    
    return {
        'mean_spacing': np.mean(spacings),
        'median_spacing': np.median(spacings),
        'std_spacing': np.std(spacings),
        'min_spacing': np.min(spacings),
        'max_spacing': np.max(spacings),
        'spacings': spacings
    }


def find_zeros_contour_integration(
    zeta_function: callable,
    real_range: Tuple[float, float],
    imag_range: Tuple[float, float],
    grid_size: int = 50
) -> List[complex]:
    """
    Find zeros using contour integration method.
    
    Uses the argument principle: number of zeros = (1/2π) * ∮ (ζ'(s)/ζ(s)) ds
    
    Parameters
    ----------
    zeta_function : callable
        Function ζ_E(s)
    real_range : Tuple[float, float]
        Range for Re(s)
    imag_range : Tuple[float, float]
        Range for Im(s)
    grid_size : int, default=50
        Grid resolution
        
    Returns
    -------
    List[complex]
        Approximate zero locations
    """
    # This is a simplified version - full implementation would use
    # numerical contour integration around grid cells
    
    real_vals = np.linspace(real_range[0], real_range[1], grid_size)
    imag_vals = np.linspace(imag_range[0], imag_range[1], grid_size)
    
    zeros = []
    threshold = 0.1
    
    for re in real_vals:
        for im in imag_vals:
            s = complex(re, im)
            try:
                zeta_val = zeta_function(s)
                if abs(zeta_val) < threshold:
                    zeros.append(s)
            except (OverflowError, RuntimeWarning):
                continue
    
    return zeros


def compare_with_classical_zeta_patterns(
    zeros: List[complex]
) -> Dict:
    """
    Compare ethical zeta zero patterns with known classical ζ(s) patterns.
    
    Parameters
    ----------
    zeros : List[complex]
        Ethical zeta zeros
        
    Returns
    -------
    dict
        Comparison metrics
    """
    if len(zeros) == 0:
        return {
            'critical_line_clustering': False,
            'spacing_regularity': np.nan,
            'similarity_score': 0.0
        }
    
    # Analyze critical line clustering
    critical_line_analysis = analyze_critical_line_proximity(zeros, critical_line=0.5)
    clusters_near_critical = critical_line_analysis['fraction_within_0.1'] > 0.5
    
    # Analyze spacing regularity
    spacing_stats = compute_spacing_distribution(zeros, sort_by='imaginary')
    spacing_cv = spacing_stats['std_spacing'] / spacing_stats['mean_spacing'] if spacing_stats['mean_spacing'] > 0 else np.nan
    spacing_regular = spacing_cv < 0.5 if not np.isnan(spacing_cv) else False
    
    # Similarity score (heuristic)
    similarity = 0.0
    if clusters_near_critical:
        similarity += 0.5
    if spacing_regular:
        similarity += 0.3
    if critical_line_analysis['fraction_within_0.05'] > 0.3:
        similarity += 0.2
    
    return {
        'critical_line_clustering': clusters_near_critical,
        'spacing_regularity': spacing_regular,
        'spacing_cv': spacing_cv,
        'similarity_score': similarity,
        'critical_line_analysis': critical_line_analysis
    }

