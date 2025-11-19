"""
Visualization Module

Provides functions for creating high-quality publication plots and interactive visualizations.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from typing import Optional, Dict, List, Tuple
import seaborn as sns


def setup_paper_style():
    """
    Configure matplotlib for paper-quality plots with LaTeX-style fonts.
    
    Examples
    --------
    >>> setup_paper_style()
    >>> # All subsequent plots will use paper style
    """
    # Use seaborn style as base
    sns.set_style("whitegrid")
    
    # Configure matplotlib for publication quality
    plt.rcParams.update({
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 14,
        'figure.dpi': 100,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,
        'lines.linewidth': 1.5,
        'axes.linewidth': 0.8,
        'grid.linewidth': 0.5,
        'grid.alpha': 0.3,
        # Try to use LaTeX rendering if available
        'text.usetex': False,  # Set to True if LaTeX is installed
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif'],
    })


def plot_Pi_B_E(
    x_values: np.ndarray,
    Pi_x: np.ndarray,
    B_x: np.ndarray,
    E_x: np.ndarray,
    title: str = "Ethical Prime Distribution",
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot Π(x), B(x), and E(x) on separate subplots.
    
    Parameters
    ----------
    x_values : np.ndarray
        Complexity values
    Pi_x : np.ndarray
        Ethical prime count function
    B_x : np.ndarray
        Baseline function
    E_x : np.ndarray
        Error function E(x) = Π(x) - B(x)
    title : str, default="Ethical Prime Distribution"
        Figure title
    save_path : Optional[str], default=None
        If specified, save figure to this path
    show : bool, default=True
        Whether to display the plot
        
    Returns
    -------
    plt.Figure
        The figure object
        
    Examples
    --------
    >>> Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
    >>> fig = plot_Pi_B_E(x_vals, Pi_x, B_x, E_x, save_path='figures/pi_b_e.pdf')
    """
    fig, axes = plt.subplots(3, 1, figsize=(10, 10))
    
    # Plot Π(x) and B(x)
    axes[0].plot(x_values, Pi_x, label=r'$\Pi(x)$ (Actual)', color='C0', linewidth=2)
    axes[0].plot(x_values, B_x, label=r'$B(x)$ (Baseline)', 
                color='C1', linestyle='--', linewidth=2)
    axes[0].set_xlabel('Complexity $x$')
    axes[0].set_ylabel('Count')
    axes[0].set_title(r'Ethical Prime Count: $\Pi(x)$ vs Baseline $B(x)$')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot E(x)
    axes[1].plot(x_values, E_x, label=r'$E(x) = \Pi(x) - B(x)$', 
                color='C2', linewidth=2)
    axes[1].axhline(y=0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    axes[1].set_xlabel('Complexity $x$')
    axes[1].set_ylabel('Error')
    axes[1].set_title(r'Error Term $E(x)$')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Plot |E(x)|
    axes[2].plot(x_values, np.abs(E_x), label=r'$|E(x)|$', 
                color='C3', linewidth=2)
    # Add reference curve: √x
    sqrt_x = np.sqrt(x_values)
    # Scale it to fit the data
    if np.max(np.abs(E_x)) > 0:
        scale = np.max(np.abs(E_x)) / np.max(sqrt_x) * 0.7
        axes[2].plot(x_values, scale * sqrt_x, label=r'$C \cdot \sqrt{x}$ (ERH)', 
                    color='gray', linestyle=':', linewidth=2)
    axes[2].set_xlabel('Complexity $x$')
    axes[2].set_ylabel('Absolute Error')
    axes[2].set_title(r'Absolute Error $|E(x)|$ vs $\sqrt{x}$ (Ethical Riemann Hypothesis)')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


def plot_error_growth(
    x_values: np.ndarray,
    E_x: np.ndarray,
    analysis: dict,
    title: str = "Error Growth Analysis",
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot |E(x)| vs x in log-log scale to visualize power law growth.
    
    Parameters
    ----------
    x_values : np.ndarray
        Complexity values
    E_x : np.ndarray
        Error values
    analysis : dict
        Output from analyze_error_growth containing fitted exponent
    title : str
        Plot title
    save_path : Optional[str]
        Save path
    show : bool
        Whether to show
        
    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    
    abs_E = np.abs(E_x)
    valid_mask = (abs_E > 0) & (x_values > 1)
    
    x_valid = x_values[valid_mask]
    E_valid = abs_E[valid_mask]
    
    # Plot data
    ax.loglog(x_valid, E_valid, 'o', label='Data', alpha=0.6, markersize=4)
    
    # Plot fitted curve if available
    if 'estimated_exponent' in analysis and not np.isnan(analysis['estimated_exponent']):
        alpha = analysis['estimated_exponent']
        C = analysis.get('constant_C', 1.0)
        x_fit = np.logspace(np.log10(x_valid.min()), np.log10(x_valid.max()), 100)
        y_fit = C * (x_fit ** alpha)
        
        ax.loglog(x_fit, y_fit, '-', label=f'Fit: $C \\cdot x^{{{alpha:.3f}}}$', 
                 linewidth=2, color='C1')
        
        # Add reference: x^0.5
        y_ref = (y_fit[0] / (x_fit[0]**0.5)) * (x_fit ** 0.5)
        ax.loglog(x_fit, y_ref, ':', label=r'Reference: $x^{0.5}$ (ERH)', 
                 linewidth=2, color='gray')
    
    ax.set_xlabel('Complexity $x$', fontsize=12)
    ax.set_ylabel(r'Absolute Error $|E(x)|$', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, which="both", alpha=0.3)
    
    # Add text box with analysis results
    if 'erh_satisfied' in analysis:
        erh_status = "Satisfied ✓" if analysis['erh_satisfied'] else "Not Satisfied ✗"
        textstr = f"ERH: {erh_status}\n"
        textstr += f"Growth Rate: {analysis.get('growth_rate', 'N/A')}\n"
        textstr += f"$R^2$: {analysis.get('r_squared', 0):.3f}"
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


def plot_spectrum(
    frequencies: np.ndarray,
    amplitudes: np.ndarray,
    peaks: Optional[List[dict]] = None,
    title: str = "Frequency Spectrum of Ethical Primes",
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot the frequency spectrum.
    
    Parameters
    ----------
    frequencies : np.ndarray
        Frequency values
    amplitudes : np.ndarray
        Amplitude values
    peaks : Optional[List[dict]]
        Peak information from analyze_spectrum_peaks
    title : str
        Plot title
    save_path : Optional[str]
        Save path
    show : bool
        Whether to show
        
    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot spectrum
    ax.plot(frequencies, amplitudes, linewidth=1.5, color='C0')
    ax.fill_between(frequencies, amplitudes, alpha=0.3, color='C0')
    
    # Mark peaks if provided
    if peaks:
        for peak in peaks[:5]:  # Show top 5 peaks
            freq = peak['frequency']
            amp = peak['amplitude']
            period = peak['period']
            
            # Find closest frequency in array
            idx = np.argmin(np.abs(frequencies - freq))
            ax.plot(freq, amplitudes[idx], 'ro', markersize=8)
            ax.annotate(f'Period: {period:.1f}', 
                       xy=(freq, amplitudes[idx]),
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=9, color='red',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    ax.set_xlabel('Frequency (cycles per complexity unit)', fontsize=12)
    ax.set_ylabel('Normalized Amplitude', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3)
    
    # Add interpretation text
    if peaks and len(peaks) > 0:
        textstr = "Dominant Periods:\n"
        for i, peak in enumerate(peaks[:3]):
            textstr += f"  {i+1}. {peak['period']:.1f} (amp: {peak['amplitude']:.2f})\n"
        
        props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
        ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', horizontalalignment='right', bbox=props)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


def plot_zero_distribution(
    zeros: List[complex],
    title: str = "Ethical Zeta Function Zeros",
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot the distribution of zeros in the complex plane.
    
    Parameters
    ----------
    zeros : List[complex]
        List of approximate zeros
    title : str
        Plot title
    save_path : Optional[str]
        Save path
    show : bool
        Whether to show
        
    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    if len(zeros) == 0:
        ax.text(0.5, 0.5, 'No zeros found', 
               ha='center', va='center', fontsize=14)
    else:
        real_parts = [z.real for z in zeros]
        imag_parts = [z.imag for z in zeros]
        
        # Scatter plot
        ax.scatter(real_parts, imag_parts, alpha=0.6, s=30, color='C0')
        
        # Add vertical line at Re(s) = 0.5 (Riemann analog)
        ax.axvline(x=0.5, color='red', linestyle='--', linewidth=2, 
                  label='Critical Line: Re(s) = 0.5')
        
        # Count zeros near critical line
        near_critical = sum(1 for r in real_parts if abs(r - 0.5) < 0.1)
        total = len(zeros)
        
        ax.set_xlabel('Re(s)', fontsize=12)
        ax.set_ylabel('Im(s)', fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add statistics text
        textstr = f"Total zeros: {total}\n"
        textstr += f"Near Re(s)=0.5: {near_critical} ({near_critical/total*100:.1f}%)"
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


def plot_judge_comparison(
    comparison: dict,
    metric: str = 'estimated_exponent',
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Create a bar chart comparing judges on a specific metric.
    
    Parameters
    ----------
    comparison : dict
        Output from compare_judges
    metric : str, default='estimated_exponent'
        Metric to compare
    title : Optional[str]
        Plot title (auto-generated if None)
    save_path : Optional[str]
        Save path
    show : bool
        Whether to show
        
    Returns
    -------
    plt.Figure
    """
    # Extract data
    names = []
    values = []
    
    for name, data in comparison.items():
        if 'error' not in data and metric in data:
            names.append(name)
            values.append(data[metric])
    
    if len(names) == 0:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f'No data for metric: {metric}', 
               ha='center', va='center', fontsize=14)
        return fig
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    colors = ['green' if metric == 'erh_satisfied' and v else 'C0' for v in values]
    bars = ax.bar(names, values, color=colors, alpha=0.7, edgecolor='black')
    
    # Add reference line for ERH exponent
    if metric == 'estimated_exponent':
        ax.axhline(y=0.5, color='red', linestyle='--', linewidth=2, 
                  label='ERH Threshold (0.5)')
        ax.legend()
    
    ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=12)
    ax.set_xlabel('Judge', fontsize=12)
    
    if title is None:
        title = f'Judge Comparison: {metric.replace("_", " ").title()}'
    ax.set_title(title, fontsize=14)
    
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


def plot_multi_judge_errors(
    comparison: dict,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot E(x) curves for multiple judges on the same axes.
    
    Parameters
    ----------
    comparison : dict
        Output from compare_error_distributions
    save_path : Optional[str]
        Save path
    show : bool
        Whether to show
        
    Returns
    -------
    plt.Figure
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot E(x)
    for name, data in comparison.items():
        if 'error' in data:
            continue
        
        x_vals = data['x_values']
        E_x = data['E_x']
        
        axes[0].plot(x_vals, E_x, label=name, linewidth=2, alpha=0.7)
    
    axes[0].axhline(y=0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    axes[0].set_xlabel('Complexity $x$', fontsize=12)
    axes[0].set_ylabel('Error $E(x)$', fontsize=12)
    axes[0].set_title('Error Terms Comparison', fontsize=14)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot |E(x)|
    for name, data in comparison.items():
        if 'error' in data:
            continue
        
        x_vals = data['x_values']
        E_x = data['E_x']
        
        axes[1].plot(x_vals, np.abs(E_x), label=name, linewidth=2, alpha=0.7)
    
    # Add reference √x
    if len(comparison) > 0:
        first_data = next(d for d in comparison.values() if 'error' not in d)
        x_vals = first_data['x_values']
        sqrt_ref = np.sqrt(x_vals)
        axes[1].plot(x_vals, sqrt_ref, ':', color='gray', linewidth=2, 
                    label=r'$\sqrt{x}$ (ERH reference)')
    
    axes[1].set_xlabel('Complexity $x$', fontsize=12)
    axes[1].set_ylabel(r'Absolute Error $|E(x)|$', fontsize=12)
    axes[1].set_title('Absolute Error Comparison', fontsize=14)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close(fig)
    
    return fig


def plot_complexity_distribution(
    actions: List,
    title: str = "Action Complexity Distribution",
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot histogram of action complexity distribution.
    
    Parameters
    ----------
    actions : List[Action]
        List of actions
    title : str
        Plot title
    save_path : Optional[str]
        Save path
    show : bool
        Whether to show
        
    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    complexities = [a.c for a in actions]
    
    ax.hist(complexities, bins=30, alpha=0.7, color='C0', edgecolor='black')
    ax.set_xlabel('Complexity', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, axis='y', alpha=0.3)
    
    # Add statistics text
    textstr = f"Mean: {np.mean(complexities):.1f}\n"
    textstr += f"Median: {np.median(complexities):.1f}\n"
    textstr += f"Std: {np.std(complexities):.1f}"
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', horizontalalignment='right', bbox=props)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close(fig)
    
    return fig

