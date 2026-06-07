"""
Algebraic Primes Module

Transitioning from heuristic prime definitions to algebraic precision.
This module defines ethical primes as singularities (high-curvature points)
on a moral manifold.
"""

import numpy as np
from typing import List, Tuple, Optional
from .action_space import Action

def compute_ethical_curvature(
    actions: List[Action],
    neighborhood_radius: int = 5
) -> np.ndarray:
    """
    Compute the "ethical curvature" at each complexity level.
    Curvature is defined as the second derivative (Laplacian) of the error landscape.
    High curvature indicates a "singularity" or structural anomaly.
    
    Parameters
    ----------
    actions : List[Action]
        Evaluated actions
    neighborhood_radius : int
        Complexity range to consider for local curvature
        
    Returns
    -------
    np.ndarray
        Curvature values for each complexity level
    """
    X_max = max(a.c for a in actions)
    x_values = np.arange(1, X_max + 1)
    
    # Aggregate errors by complexity
    errors_by_c = {}
    for a in actions:
        if a.delta is not None:
            errors_by_c.setdefault(a.c, []).append(abs(a.delta))
    
    mean_error = np.zeros(X_max)
    for x in x_values:
        if x in errors_by_c:
            mean_error[x-1] = np.mean(errors_by_c[x])
        else:
            # Linear interpolation for missing complexity values
            mean_error[x-1] = 0.0
            
    # Compute second derivative (curvature)
    curvature = np.gradient(np.gradient(mean_error))
    
    return curvature

def select_primes_by_singularity(
    actions: List[Action],
    curvature_threshold: float = 2.0,
    neighborhood_radius: int = 5
) -> List[Action]:
    """
    Select ethical primes as "singularities" on the moral manifold.
    Uses high-curvature points (anomalous error growth) as the formal definition.
    
    Parameters
    ----------
    actions : List[Action]
        Evaluated actions
    curvature_threshold : float
        Multiple of standard deviation to consider as a singularity
    neighborhood_radius : int
        Radius for curvature computation
        
    Returns
    -------
    List[Action]
        Subset of actions identified as algebraic primes
    """
    if not actions:
        return []
        
    curvature = compute_ethical_curvature(actions, neighborhood_radius)
    curv_mean = np.mean(np.abs(curvature))
    curv_std = np.std(np.abs(curvature))
    
    threshold = curv_mean + curvature_threshold * curv_std
    
    # Identify complexity levels with high curvature
    singular_complexities = np.where(np.abs(curvature) > threshold)[0] + 1
    
    # Select actions at these complexities that are also mistakes
    primes = [
        a for a in actions 
        if a.c in singular_complexities and a.mistake_flag == 1
    ]
    
    # If no high-curvature points found, fallback to top-weighted mistakes
    if not primes:
        mistakes = [a for a in actions if a.mistake_flag == 1]
        mistakes.sort(key=lambda a: a.w, reverse=True)
        primes = mistakes[:max(1, len(mistakes) // 10)]
        
    return primes

def get_manifold_topology_metrics(actions: List[Action]) -> dict:
    """
    Compute topological metrics of the moral manifold.
    
    Returns:
        Roughness (RMS curvature)
        Singularity Density (Primes / complexity range)
        Moral Euler Characteristic (Mock topological invariant)
    """
    curvature = compute_ethical_curvature(actions)
    roughness = np.sqrt(np.mean(curvature**2))
    
    primes = select_primes_by_singularity(actions)
    X_max = max(a.c for a in actions) if actions else 1
    density = len(primes) / X_max
    
    # Mock Euler characteristic: V - E + F
    # In this context, nodes are complexities, edges are transitions
    # We define it as a measure of structural stability
    euler_char = 1.0 - roughness + density
    
    return {
        "manifold_roughness": float(roughness),
        "singularity_density": float(density),
        "moral_euler_characteristic": float(euler_char)
    }
