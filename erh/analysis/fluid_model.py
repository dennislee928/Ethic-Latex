"""
Fluid Model Module

This module implements continuous fluid/field models for error density evolution,
using partial differential equations to describe how moral judgment errors
propagate and evolve in complexity-time space.

The model is based on:
∂u/∂t + ∂/∂x(v·u) = D·∂²u/∂x² - α·u + S(x,t)

where:
- u(x,t): error density at complexity x, time t
- v: convection velocity (error growth trend)
- D: diffusion coefficient (error propagation)
- α: natural correction rate
- S(x,t): source term (new error generation)
"""

import numpy as np
from typing import Tuple, Optional, Dict, Callable, List
from scipy import sparse
from scipy.sparse.linalg import spsolve
try:
    from scipy.integrate import solve_ivp
    SCIPY_IVP_AVAILABLE = True
except ImportError:
    SCIPY_IVP_AVAILABLE = False


def solve_error_density_pde(
    x_range: Tuple[float, float],
    t_range: Tuple[float, float],
    nx: int = 100,
    nt: int = 100,
    v: float = 0.1,
    D: float = 0.01,
    alpha: float = 0.05,
    S: Optional[Callable] = None,
    initial_condition: Optional[np.ndarray] = None,
    boundary_conditions: str = 'neumann'
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Solve the error density PDE using finite difference method.
    
    Solves: ∂u/∂t + ∂/∂x(v·u) = D·∂²u/∂x² - α·u + S(x,t)
    
    Parameters
    ----------
    x_range : Tuple[float, float]
        Complexity range (x_min, x_max)
    t_range : Tuple[float, float]
        Time range (t_min, t_max)
    nx : int, default=100
        Number of spatial grid points
    nt : int, default=100
        Number of time steps
    v : float, default=0.1
        Convection velocity (error growth trend)
    D : float, default=0.01
        Diffusion coefficient
    alpha : float, default=0.05
        Natural correction rate
    S : Optional[Callable], default=None
        Source term function S(x, t). If None, uses zero source.
    initial_condition : Optional[np.ndarray], default=None
        Initial condition u(x, 0). If None, uses Gaussian profile.
    boundary_conditions : str, default='neumann'
        Boundary condition type: 'neumann' (zero flux) or 'dirichlet' (zero value)
        
    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        (u_xt, x_grid, t_grid)
        - u_xt: 2D array of shape (nt, nx) with solution
        - x_grid: 1D array of x values
        - t_grid: 1D array of t values
        
    Examples
    --------
    >>> x_range = (0, 100)
    >>> t_range = (0, 10)
    >>> u_xt, x_vals, t_vals = solve_error_density_pde(x_range, t_range, nx=50, nt=50)
    """
    x_min, x_max = x_range
    t_min, t_max = t_range
    
    # Grid
    x_grid = np.linspace(x_min, x_max, nx)
    t_grid = np.linspace(t_min, t_max, nt)
    dx = (x_max - x_min) / (nx - 1)
    dt = (t_max - t_min) / (nt - 1)
    
    # Initialize solution
    u_xt = np.zeros((nt, nx))
    
    # Initial condition
    if initial_condition is not None:
        u_xt[0, :] = initial_condition
    else:
        # Gaussian profile centered at mid-complexity
        x_center = (x_min + x_max) / 2
        sigma = (x_max - x_min) / 10
        u_xt[0, :] = np.exp(-((x_grid - x_center) ** 2) / (2 * sigma ** 2))
    
    # Source term function
    if S is None:
        def S_func(x, t):
            return 0.0
    else:
        S_func = S
    
    # Time stepping using implicit-explicit scheme
    for n in range(nt - 1):
        u_n = u_xt[n, :]
        t_n = t_grid[n]
        
        # Build matrices for implicit part (diffusion and correction)
        # Implicit: D·∂²u/∂x² - α·u
        A = sparse.diags([-2*D/dx**2 - alpha], [0], shape=(nx, nx), format='csr')
        A += sparse.diags([D/dx**2], [1], shape=(nx, nx), format='csr')
        A += sparse.diags([D/dx**2], [-1], shape=(nx, nx), format='csr')
        
        # Boundary conditions
        if boundary_conditions == 'neumann':
            # Zero flux: ∂u/∂x = 0 at boundaries
            A[0, 0] = -D/dx**2 - alpha
            A[0, 1] = D/dx**2
            A[-1, -1] = -D/dx**2 - alpha
            A[-1, -2] = D/dx**2
        else:  # dirichlet
            # Zero value at boundaries
            A[0, :] = 0
            A[0, 0] = 1
            A[-1, :] = 0
            A[-1, -1] = 1
        
        # Explicit part: -∂/∂x(v·u) + S
        # Upwind scheme for convection
        conv_term = np.zeros(nx)
        for i in range(1, nx):
            if v > 0:
                conv_term[i] = -v * (u_n[i] - u_n[i-1]) / dx
            else:
                if i < nx - 1:
                    conv_term[i] = -v * (u_n[i+1] - u_n[i]) / dx
        
        # Source term
        source_term = np.array([S_func(x, t_n) for x in x_grid])
        
        # Right-hand side
        b = u_n + dt * (conv_term + source_term)
        
        # Apply boundary conditions to RHS
        if boundary_conditions == 'dirichlet':
            b[0] = 0
            b[-1] = 0
        
        # Solve: (I - dt*A) * u_{n+1} = b
        I = sparse.eye(nx, format='csr')
        system_matrix = I - dt * A
        
        try:
            u_next = spsolve(system_matrix, b)
            u_xt[n+1, :] = u_next
        except:
            # Fallback: explicit Euler if solve fails
            u_xt[n+1, :] = u_n + dt * (conv_term + source_term - alpha * u_n)
    
    return u_xt, x_grid, t_grid


def detect_critical_phenomena(
    u_xt: np.ndarray,
    x_grid: np.ndarray,
    t_grid: np.ndarray,
    threshold: float = 2.0
) -> List[Dict]:
    """
    Detect critical phenomena: sudden jumps in error density.
    
    Parameters
    ----------
    u_xt : np.ndarray
        Error density array
    x_grid : np.ndarray
        Complexity grid
    t_grid : np.ndarray
        Time grid
    threshold : float, default=2.0
        Threshold multiplier for critical detection
        
    Returns
    -------
    List[Dict]
        List of critical events, each containing:
        - 'time': time index
        - 'complexity': complexity value
        - 'density_jump': magnitude of jump
        - 'severity': severity level
    """
    critical_events = []
    nt, nx = u_xt.shape
    
    mean_density = np.mean(u_xt)
    std_density = np.std(u_xt)
    threshold_value = mean_density + threshold * std_density
    
    for t in range(1, nt):
        for x_idx in range(nx):
            current_density = u_xt[t, x_idx]
            prev_density = u_xt[t-1, x_idx]
            
            # Check for sudden jump
            if current_density > threshold_value:
                jump = current_density - prev_density
                
                if jump > std_density:
                    # Determine severity
                    if jump > 3 * std_density:
                        severity = 'critical'
                    elif jump > 2 * std_density:
                        severity = 'high'
                    else:
                        severity = 'medium'
                    
                    critical_events.append({
                        'time': t,
                        'time_value': t_grid[t],
                        'complexity': x_grid[x_idx],
                        'density': current_density,
                        'density_jump': jump,
                        'severity': severity
                    })
    
    return critical_events


def fit_fluid_parameters(
    E_xt: np.ndarray,
    x_values: np.ndarray,
    t_values: np.ndarray
) -> Dict[str, float]:
    """
    Fit fluid model parameters from observed error data.
    
    Parameters
    ----------
    E_xt : np.ndarray
        Observed error array
    x_values : np.ndarray
        Complexity values
    t_values : np.ndarray
        Time values
        
    Returns
    -------
    Dict[str, float]
        Fitted parameters:
        - 'v': convection velocity
        - 'D': diffusion coefficient
        - 'alpha': correction rate
    """
    # Estimate parameters from data
    # v: average rate of error growth with complexity
    # D: spread of errors across complexity
    # alpha: decay rate over time
    
    # Estimate v: correlation between complexity and error magnitude
    error_magnitudes = np.abs(E_xt)
    mean_errors = np.mean(error_magnitudes, axis=0)
    
    if len(x_values) > 1 and np.std(mean_errors) > 0:
        # Linear fit: mean_error ~ v * x
        coeffs = np.polyfit(x_values, mean_errors, 1)
        v_estimate = max(0.01, min(1.0, abs(coeffs[0])))
    else:
        v_estimate = 0.1
    
    # Estimate D: variance across complexity
    error_variance = np.var(error_magnitudes, axis=0)
    mean_variance = np.mean(error_variance)
    D_estimate = max(0.001, min(0.1, mean_variance / 10))
    
    # Estimate alpha: decay rate over time
    if E_xt.shape[0] > 1:
        time_decay = []
        for x_idx in range(E_xt.shape[1]):
            errors_over_time = error_magnitudes[:, x_idx]
            if len(errors_over_time) > 1 and np.max(errors_over_time) > 0:
                # Exponential decay fit
                try:
                    log_errors = np.log(errors_over_time + 1e-10)
                    time_vals = np.arange(len(errors_over_time))
                    coeffs = np.polyfit(time_vals, log_errors, 1)
                    decay_rate = -coeffs[0]
                    if decay_rate > 0:
                        time_decay.append(decay_rate)
                except:
                    pass
        
        alpha_estimate = np.mean(time_decay) if time_decay else 0.05
        alpha_estimate = max(0.001, min(0.5, alpha_estimate))
    else:
        alpha_estimate = 0.05
    
    return {
        'v': v_estimate,
        'D': D_estimate,
        'alpha': alpha_estimate
    }


def compute_steady_state(
    v: float,
    D: float,
    alpha: float,
    S: Callable,
    x_range: Tuple[float, float],
    nx: int = 100
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute steady-state solution (∂u/∂t = 0).
    
    Parameters
    ----------
    v : float
        Convection velocity
    D : float
        Diffusion coefficient
    alpha : float
        Correction rate
    S : Callable
        Source term function S(x)
    x_range : Tuple[float, float]
        Complexity range
    nx : int, default=100
        Number of grid points
        
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (u_steady, x_grid) - steady-state solution
    """
    x_min, x_max = x_range
    x_grid = np.linspace(x_min, x_max, nx)
    dx = (x_max - x_min) / (nx - 1)
    
    # Steady-state equation: D·∂²u/∂x² - v·∂u/∂x - α·u + S = 0
    # Rearranged: D·∂²u/∂x² - v·∂u/∂x - α·u = -S
    
    # Build matrix
    A = sparse.diags([-2*D/dx**2 - alpha], [0], shape=(nx, nx), format='csr')
    A += sparse.diags([D/dx**2 + v/(2*dx)], [1], shape=(nx, nx), format='csr')
    A += sparse.diags([D/dx**2 - v/(2*dx)], [-1], shape=(nx, nx), format='csr')
    
    # Boundary conditions (Neumann: zero flux)
    A[0, 0] = -D/dx**2 - alpha
    A[0, 1] = D/dx**2 + v/(2*dx)
    A[-1, -1] = -D/dx**2 - alpha
    A[-1, -2] = D/dx**2 - v/(2*dx)
    
    # Source term
    b = -np.array([S(x) for x in x_grid])
    
    # Solve
    try:
        u_steady = spsolve(A, b)
    except Exception:
        # Fallback: simple approximation
        u_steady = np.array([S(x) / alpha for x in x_grid])
    return u_steady, x_grid