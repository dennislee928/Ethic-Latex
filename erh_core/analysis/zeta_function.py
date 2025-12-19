"""
Ethical Zeta Function Module

This module implements the "ethical zeta function" - a generating function
inspired by the Riemann zeta function that encodes the distribution of ethical primes.

It also provides spectrum analysis via FFT to detect periodic patterns in judgment errors.
"""

import numpy as np
from typing import List, Tuple, Optional
import warnings


def build_m_sequence(
    primes: List,
    X_max: int = 200,
    mode: str = 'count'
) -> np.ndarray:
    """
    Build the sequence m(n) representing ethical prime distribution.
    
    m(n) = number of ethical primes at complexity level n
    
    Parameters
    ----------
    primes : List[Action]
        List of ethical primes
    X_max : int, default=200
        Maximum complexity to consider
    mode : str, default='count'
        How to build the sequence:
        - 'count': m(n) = count of primes at complexity n
        - 'weighted': m(n) = sum of importance weights at complexity n
        - 'error': m(n) = sum of |error| at complexity n
        
    Returns
    -------
    np.ndarray
        Array of length X_max where m[n] represents the value at complexity n
        
    Examples
    --------
    >>> primes = select_ethical_primes(actions)
    >>> m = build_m_sequence(primes, X_max=100)
    >>> print(f"Distribution: {m[:20]}")
    """
    m = np.zeros(X_max, dtype=float)
    
    for prime in primes:
        if 0 < prime.c < X_max:
            if mode == 'count':
                m[prime.c] += 1
            elif mode == 'weighted':
                m[prime.c] += prime.w
            elif mode == 'error':
                m[prime.c] += abs(prime.delta) if prime.delta is not None else 0
            else:
                raise ValueError(f"Unknown mode: {mode}")
    
    return m


def ethical_zeta_product(
    primes: List,
    s: complex,
    max_terms: int = 100
) -> complex:
    """
    Compute the ethical zeta function via Euler product formula.
    
    ζ_E(s) = ∏_{p ∈ P} 1 / (1 - c(p)^{-s})
    
    This is a toy model inspired by the Euler product for ζ(s).
    
    Parameters
    ----------
    primes : List[Action]
        List of ethical primes
    s : complex
        Complex argument (typically Re(s) > 1 for convergence)
    max_terms : int, default=100
        Maximum number of terms to include
        
    Returns
    -------
    complex
        Value of ζ_E(s)
        
    Examples
    --------
    >>> primes = select_ethical_primes(actions)
    >>> zeta_2 = ethical_zeta_product(primes, s=2.0)
    >>> print(f"ζ_E(2) = {zeta_2}")
    
    Notes
    -----
    This is a heuristic construction. In the real Riemann zeta function,
    the product runs over all primes. Here we use "ethical primes" instead.
    
    Convergence requires Re(s) > 1 typically.
    """
    if len(primes) == 0:
        return 1.0
    
    # Take up to max_terms primes
    primes_subset = primes[:min(max_terms, len(primes))]
    
    product = 1.0 + 0j
    
    for prime in primes_subset:
        c = prime.c
        if c > 0:
            try:
                term = 1.0 / (1.0 - c**(-s))
                product *= term
            except (OverflowError, ZeroDivisionError):
                # Skip terms that cause numerical issues
                continue
    
    return product


def ethical_zeta_sum(
    m: np.ndarray,
    s: complex
) -> complex:
    """
    Compute ethical zeta via Dirichlet series (sum form).
    
    ζ_E(s) = ∑_{n=1}^{N} m(n) / n^s
    
    Parameters
    ----------
    m : np.ndarray
        Sequence m(n) from build_m_sequence
    s : complex
        Complex argument
        
    Returns
    -------
    complex
        Value of ζ_E(s)
    """
    N = len(m)
    result = 0j
    
    for n in range(1, N):
        if m[n] != 0:
            result += m[n] / (n ** s)
    
    return result


def find_approximate_zeros(
    m: np.ndarray,
    real_range: Tuple[float, float] = (0.3, 0.7),
    imag_range: Tuple[float, float] = (0, 50),
    grid_size: int = 50,
    threshold: float = 0.1,
    refine: bool = False
) -> List[complex]:
    """
    Find approximate zeros of the ethical zeta function by grid search.
    
    Scans a grid in the complex plane and finds points where |ζ_E(s)| < threshold.
    
    Parameters
    ----------
    m : np.ndarray
        Sequence from build_m_sequence
    real_range : Tuple[float, float], default=(0.3, 0.7)
        Range for Re(s)
    imag_range : Tuple[float, float], default=(0, 50)
        Range for Im(s)
    grid_size : int, default=50
        Number of points per dimension
    threshold : float, default=0.1
        Threshold for considering |ζ_E(s)| ≈ 0
    refine : bool, default=False
        If True, refine zeros using Newton-Raphson method
        
    Returns
    -------
    List[complex]
        List of approximate zeros
        
    Examples
    --------
    >>> m = build_m_sequence(primes, X_max=100)
    >>> zeros = find_approximate_zeros(m, grid_size=30)
    >>> print(f"Found {len(zeros)} approximate zeros")
    >>> for z in zeros[:5]:
    ...     print(f"  s = {z:.3f}")
    
    Notes
    -----
    The Riemann Hypothesis states that all non-trivial zeros of ζ(s) have Re(s) = 1/2.
    By analogy, we might expect ethical zeta zeros to cluster near some critical line.
    """
    real_vals = np.linspace(real_range[0], real_range[1], grid_size)
    imag_vals = np.linspace(imag_range[0], imag_range[1], grid_size)
    
    zeros = []
    
    for re in real_vals:
        for im in imag_vals:
            s = complex(re, im)
            try:
                zeta_val = ethical_zeta_sum(m, s)
                if abs(zeta_val) < threshold:
                    zeros.append(s)
            except (OverflowError, RuntimeWarning):
                continue
    
    # Refine zeros if requested
    if refine and len(zeros) > 0:
        try:
            from .zeta_zeros_analysis import refine_zero_newton_raphson
            refined_zeros = []
            zeta_func = lambda s: ethical_zeta_sum(m, s)
            for zero in zeros:
                refined = refine_zero_newton_raphson(zeta_func, zero)
                if refined is not None:
                    refined_zeros.append(refined)
                else:
                    refined_zeros.append(zero)  # Keep original if refinement fails
            zeros = refined_zeros
        except ImportError:
            pass  # Refinement not available
    
    return zeros


def compute_spectrum(
    m: np.ndarray,
    normalize: bool = True
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the Fourier spectrum of the ethical prime distribution.
    
    This reveals periodic patterns in how misjudgments are distributed
    across complexity levels.
    
    Parameters
    ----------
    m : np.ndarray
        Sequence m(n) from build_m_sequence
    normalize : bool, default=True
        If True, normalize amplitudes to [0, 1]
        
    Returns
    -------
    frequencies : np.ndarray
        Frequency values (cycles per complexity unit)
    amplitudes : np.ndarray
        Amplitude (magnitude) of each frequency component
        
    Examples
    --------
    >>> m = build_m_sequence(primes, X_max=200)
    >>> freqs, amps = compute_spectrum(m)
    >>> dominant_freq = freqs[np.argmax(amps)]
    >>> print(f"Dominant frequency: {dominant_freq:.3f}")
    
    Notes
    -----
    Strong peaks in the spectrum indicate periodic patterns in misjudgments.
    For example, a peak at frequency f means errors tend to cluster every 1/f
    complexity units.
    
    This is analogous to studying the "spectrum of primes" in number theory.
    """
    # Apply FFT
    spectrum = np.fft.fft(m)
    
    # Get frequencies
    N = len(m)
    frequencies = np.fft.fftfreq(N)
    
    # Compute amplitudes (magnitude)
    amplitudes = np.abs(spectrum)
    
    # Only keep positive frequencies
    positive_mask = frequencies >= 0
    frequencies = frequencies[positive_mask]
    amplitudes = amplitudes[positive_mask]
    
    # Normalize if requested
    if normalize and np.max(amplitudes) > 0:
        amplitudes = amplitudes / np.max(amplitudes)
    
    return frequencies, amplitudes


def compute_power_spectrum(
    m: np.ndarray,
    smoothing: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the power spectrum (squared magnitude).
    
    Parameters
    ----------
    m : np.ndarray
        Sequence from build_m_sequence
    smoothing : Optional[int], default=None
        If specified, apply moving average smoothing with this window size
        
    Returns
    -------
    frequencies : np.ndarray
        Frequency values
    power : np.ndarray
        Power at each frequency
    """
    frequencies, amplitudes = compute_spectrum(m, normalize=False)
    power = amplitudes ** 2
    
    if smoothing is not None and smoothing > 1:
        # Apply moving average
        window = np.ones(smoothing) / smoothing
        power = np.convolve(power, window, mode='same')
    
    return frequencies, power


def analyze_spectrum_peaks(
    frequencies: np.ndarray,
    amplitudes: np.ndarray,
    num_peaks: int = 5,
    min_freq: float = 0.01
) -> List[dict]:
    """
    Identify and analyze dominant peaks in the spectrum.
    
    Parameters
    ----------
    frequencies : np.ndarray
        Frequency values from compute_spectrum
    amplitudes : np.ndarray
        Amplitude values from compute_spectrum
    num_peaks : int, default=5
        Number of top peaks to return
    min_freq : float, default=0.01
        Minimum frequency to consider (exclude DC component)
        
    Returns
    -------
    List[dict]
        List of peak information dictionaries, sorted by amplitude
        Each dict contains: 'frequency', 'amplitude', 'period'
        
    Examples
    --------
    >>> freqs, amps = compute_spectrum(m)
    >>> peaks = analyze_spectrum_peaks(freqs, amps, num_peaks=3)
    >>> for peak in peaks:
    ...     print(f"Period: {peak['period']:.1f}, Amplitude: {peak['amplitude']:.3f}")
    """
    # Filter out low frequencies
    mask = frequencies >= min_freq
    freqs_filtered = frequencies[mask]
    amps_filtered = amplitudes[mask]
    
    if len(amps_filtered) == 0:
        return []
    
    # Find peaks (local maxima)
    peaks_info = []
    
    # Simple approach: find top N amplitudes
    sorted_indices = np.argsort(amps_filtered)[::-1]  # descending
    
    for i in range(min(num_peaks, len(sorted_indices))):
        idx = sorted_indices[i]
        freq = freqs_filtered[idx]
        amp = amps_filtered[idx]
        
        # Period = 1 / frequency
        period = 1.0 / freq if freq > 0 else np.inf
        
        peaks_info.append({
            'frequency': freq,
            'amplitude': amp,
            'period': period
        })
    
    return peaks_info


def compute_zeta_grid(
    m: np.ndarray,
    real_range: Tuple[float, float] = (0.1, 1.5),
    imag_range: Tuple[float, float] = (0, 30),
    grid_size: int = 100
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute |ζ_E(s)| on a grid in the complex plane for visualization.
    
    Parameters
    ----------
    m : np.ndarray
        Sequence from build_m_sequence
    real_range : Tuple[float, float]
        Range for Re(s)
    imag_range : Tuple[float, float]
        Range for Im(s)
    grid_size : int, default=100
        Number of points per dimension
        
    Returns
    -------
    real_grid : np.ndarray
        2D array of real parts
    imag_grid : np.ndarray
        2D array of imaginary parts
    magnitude_grid : np.ndarray
        2D array of |ζ_E(s)| values
        
    Examples
    --------
    >>> m = build_m_sequence(primes)
    >>> real, imag, mag = compute_zeta_grid(m, grid_size=50)
    >>> plt.contourf(real, imag, np.log(mag + 1))
    >>> plt.colorbar(label='log|ζ_E(s)|')
    >>> plt.xlabel('Re(s)')
    >>> plt.ylabel('Im(s)')
    >>> plt.show()
    """
    real_vals = np.linspace(real_range[0], real_range[1], grid_size)
    imag_vals = np.linspace(imag_range[0], imag_range[1], grid_size)
    
    real_grid, imag_grid = np.meshgrid(real_vals, imag_vals)
    magnitude_grid = np.zeros_like(real_grid)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        for i in range(grid_size):
            for j in range(grid_size):
                s = complex(real_grid[i, j], imag_grid[i, j])
                try:
                    zeta_val = ethical_zeta_sum(m, s)
                    magnitude_grid[i, j] = abs(zeta_val)
                except:
                    magnitude_grid[i, j] = np.nan
    
    return real_grid, imag_grid, magnitude_grid


def detect_periodic_bias(
    m: np.ndarray,
    significance_threshold: float = 0.3
) -> dict:
    """
    Detect if there's a significant periodic structure in misjudgments.
    
    Parameters
    ----------
    m : np.ndarray
        Sequence from build_m_sequence
    significance_threshold : float, default=0.3
        Threshold for considering a frequency peak significant
        
    Returns
    -------
    dict
        Analysis results including:
        - 'has_periodic_bias': bool
        - 'dominant_period': float or None
        - 'periodicity_strength': float
        - 'top_periods': List[float]
    """
    freqs, amps = compute_spectrum(m, normalize=True)
    peaks = analyze_spectrum_peaks(freqs, amps, num_peaks=5)
    
    has_bias = len(peaks) > 0 and peaks[0]['amplitude'] > significance_threshold
    
    result = {
        'has_periodic_bias': has_bias,
        'dominant_period': peaks[0]['period'] if peaks else None,
        'periodicity_strength': peaks[0]['amplitude'] if peaks else 0.0,
        'top_periods': [p['period'] for p in peaks],
        'top_amplitudes': [p['amplitude'] for p in peaks],
        'interpretation': ''
    }
    
    # Add interpretation
    if has_bias:
        period = result['dominant_period']
        result['interpretation'] = (
            f"Strong periodic pattern detected: errors cluster every ~{period:.1f} "
            f"complexity units. This suggests structural bias in the judgment system."
        )
    else:
        result['interpretation'] = (
            "No strong periodic pattern detected. Errors appear relatively "
            "uniformly distributed across complexity levels."
        )
    
    return result

