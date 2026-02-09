"""
Visualization Module

Provides functions for creating high-quality publication plots and interactive visualizations.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from typing import Optional, Dict, List, Tuple
import seaborn as sns

try:
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
except ImportError:
    Axes3D = None


def setup_paper_style():
    """
    Configure matplotlib for paper-quality plots with LaTeX-style fonts.
    
    Examples
    --------
    >>> setup_paper_style()
    >>> # All subsequent plots will use paper style
    """
    # Use seaborn style for publication quality
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
        
        # Add annotation highlighting key observation
        if alpha < 0.5:
            # Better than ERH bound
            mid_idx = len(x_fit) // 2
            ax.annotate(f'Better than ERH\n($\\alpha={alpha:.3f}<0.5$)', 
                       xy=(x_fit[mid_idx], y_fit[mid_idx]),
                       xytext=(x_fit[mid_idx]*1.5, y_fit[mid_idx]*0.5),
                       arrowprops=dict(arrowstyle='->', color='green', lw=1.5),
                       fontsize=10, color='green', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))
        elif alpha > 0.6:
            # Violates ERH bound
            mid_idx = len(x_fit) // 2
            ax.annotate(f'ERH violation\n($\\alpha={alpha:.3f}>0.5$)', 
                       xy=(x_fit[mid_idx], y_fit[mid_idx]),
                       xytext=(x_fit[mid_idx]*1.5, y_fit[mid_idx]*1.5),
                       arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                       fontsize=10, color='red', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.7))
    
    ax.set_xlabel('Complexity $x$', fontsize=12)
    ax.set_ylabel(r'Absolute Error $|E(x)|$', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, which="both", alpha=0.3)
    
    # Add text box with analysis results
    if 'estimated_exponent' in analysis:
        alpha = analysis['estimated_exponent']
        within_bound = alpha <= 0.5 + 0.15  # Allow small tolerance
        if within_bound:
            if alpha < 0.5:
                textstr = f"ERH-style bound: satisfied\n(better-than-bound, $\\alpha = {alpha:.3f} < 0.5$)\n"
            else:
                textstr = f"ERH-style bound: satisfied\n($\\alpha = {alpha:.3f} \\approx 0.5$)\n"
        else:
            textstr = f"ERH-style bound: not satisfied\n($\\alpha = {alpha:.3f} > 0.5$)\n"
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
    ax.bar(names, values, color=colors, alpha=0.7, edgecolor='black')
    
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
    
    Uses colorblind-friendly palette and different line styles/markers
    for accessibility.
    
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
    # Colorblind-friendly palette (Okabe-Ito palette)
    colors = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7']
    # Different line styles for additional distinction
    linestyles = ['-', '--', '-.', ':', '-', '--', '-.']
    # Different markers for even more distinction
    markers = ['o', 's', '^', 'D', 'v', 'p', '*']
    
    # Get sample x_vals length for marker spacing (use first valid data)
    sample_length = 100  # Default
    for data in comparison.values():
        if 'error' not in data and 'x_values' in data:
            sample_length = len(data['x_values'])
            break
    marker_styles = [{'marker': m, 'markevery': max(1, sample_length//20)} for m in markers]
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot E(x)
    for idx, (name, data) in enumerate(comparison.items()):
        if 'error' in data:
            continue
        
        x_vals = data['x_values']
        E_x = data['E_x']
        
        color = colors[idx % len(colors)]
        linestyle = linestyles[idx % len(linestyles)]
        marker_style = marker_styles[idx % len(marker_styles)]
        
        axes[0].plot(x_vals, E_x, label=name, linewidth=2, alpha=0.8,
                    color=color, linestyle=linestyle, **marker_style)
    
    axes[0].axhline(y=0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
    axes[0].set_xlabel('Complexity $x$', fontsize=12)
    axes[0].set_ylabel('Error $E(x)$', fontsize=12)
    axes[0].set_title('Error Terms Comparison', fontsize=14)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot |E(x)|
    for idx, (name, data) in enumerate(comparison.items()):
        if 'error' in data:
            continue
        
        x_vals = data['x_values']
        E_x = data['E_x']
        
        color = colors[idx % len(colors)]
        linestyle = linestyles[idx % len(linestyles)]
        marker_style = marker_styles[idx % len(marker_styles)]
        
        axes[1].plot(x_vals, np.abs(E_x), label=name, linewidth=2, alpha=0.8,
                    color=color, linestyle=linestyle, **marker_style)
    
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
    
    # Add annotation for fastest/slowest decay
    if len(comparison) > 1:
        # Find judge with fastest decay (lowest error at max x)
        valid_data = [(name, data) for name, data in comparison.items() if 'error' not in data]
        if len(valid_data) > 0:
            max_x_idx = -1
            fastest_judge = None
            min_error = float('inf')
            
            for name, data in valid_data:
                x_vals = data['x_values']
                abs_E = np.abs(data['E_x'])
                if len(abs_E) > 0:
                    final_error = abs_E[max_x_idx]
                    if final_error < min_error:
                        min_error = final_error
                        fastest_judge = (name, data, x_vals[max_x_idx])
            
            # Annotate fastest decay
            if fastest_judge:
                name, data, x_val = fastest_judge
                abs_E = np.abs(data['E_x'])
                y_val = abs_E[max_x_idx]
                axes[1].annotate(f'Fastest decay:\n{name}', 
                               xy=(x_val, y_val),
                               xytext=(x_val*1.3, y_val*2),
                               arrowprops=dict(arrowstyle='->', color='green', lw=1.5),
                               fontsize=9, color='green', weight='bold',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.6))
    
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


def plot_critical_bound(
    comparison: Dict[str, dict],
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot 1: The Critical Bound.

    X-axis: Complexity x (Log Scale).
    Y-axis: Error Magnitude |E(x)| (Log Scale).
    Overlay: y = x^(1/2) (Riemann Bound).
    Different agents (Conservative vs. Aggressive).
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2"]

    for idx, (name, data) in enumerate(comparison.items()):
        if "error" in data or "x_values" not in data:
            continue
        x_vals = np.array(data["x_values"])
        E_x = np.array(data["E_x"])
        abs_E = np.abs(E_x)
        valid = (abs_E > 0) & (x_vals > 1)
        if np.sum(valid) < 2:
            continue
        x_v, y_v = x_vals[valid], abs_E[valid]
        ax.loglog(x_v, y_v, "o-", label=name, alpha=0.7, color=colors[idx % len(colors)])

    if len(comparison) > 0:
        first = next((d for d in comparison.values() if "error" not in d and "x_values" in d), None)
        if first is not None:
            x_vals = np.array(first["x_values"])
            x_ref = np.linspace(max(1, x_vals.min()), x_vals.max(), 100)
            scale = 1.0
            if np.max(np.abs(first["E_x"])) > 0:
                scale = np.median(np.abs(first["E_x"])[np.abs(first["E_x"]) > 0]) / (
                    np.median(x_vals[x_vals > 1]) ** 0.5
                )
            y_ref = scale * np.sqrt(x_ref)
            ax.loglog(x_ref, y_ref, ":", color="gray", linewidth=2, label=r"$C \cdot x^{1/2}$ (ERH)")

    ax.set_xlabel("Complexity $x$ (Log Scale)", fontsize=12)
    ax.set_ylabel(r"Error Magnitude $|E(x)|$ (Log Scale)", fontsize=12)
    ax.set_title("The Critical Bound: $|E(x)|$ vs. $x^{1/2}$")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_phase_transition(
    data: dict,
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot phase transition: Coupling Strength J vs Ethical Stability.

    X-axis: Coupling Strength ($J$)
    Y-axis: Ethical Stability (1 - Error Rate)
    Marks critical point J_c where stability drops.

    Parameters
    ----------
    data : dict
        From run_phase_transition_exp: coupling_strengths, error_rates,
        stability, critical_point_J, fidelities.
    save_path : Optional[str]
        Path to save figure.
    show : bool
        Whether to display.
    """
    sns.set_style("whitegrid")
    J = np.array(data.get("coupling_strengths", []))
    if len(J) == 0 and "error_rates" in data:
        J = np.arange(len(data["error_rates"]))
    error_rates = np.array(data.get("error_rates", []))
    stability = np.array(data.get("stability", 1.0 - error_rates)) if len(error_rates) else np.array([])
    fidelities = np.array(data.get("fidelities", []))
    critical_point = data.get("critical_point_J")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(J, stability, "o-", label="Ethical Stability (1 - Error Rate)", linewidth=2)
    if len(fidelities) == len(J):
        ax.plot(J, fidelities, "s--", label="Quantum Fidelity", alpha=0.8)
    if critical_point is not None:
        ax.axvline(
            x=critical_point,
            color="red",
            linestyle="--",
            alpha=0.8,
            label=f"Critical point $J_c \\approx {critical_point:.2f}$",
        )
    ax.set_xlabel("Coupling Strength $J$", fontsize=12)
    ax.set_ylabel("Ethical Stability / Fidelity", fontsize=12)
    ax.set_title("Phase Transition: Ethical Stability vs Coupling Strength")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_phase_transition_diagram(
    conflict_densities: np.ndarray,
    fidelities: np.ndarray,
    coherences: Optional[np.ndarray] = None,
    collapse_point: Optional[float] = None,
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot 2: Phase Transition Diagram.

    X-axis: Conflict Density (Complexity).
    Y-axis: Quantum State Fidelity (or System Coherence).
    Highlight the "Collapse Point" (Pole).
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(conflict_densities, fidelities, "o-", label="Ground State Fidelity", linewidth=2)
    if coherences is not None:
        ax.plot(conflict_densities, coherences, "s--", label="Consensus Coherence", alpha=0.8)
    ax.axhline(y=0.3, color="gray", linestyle=":", alpha=0.7)
    if collapse_point is not None:
        ax.axvline(
            x=collapse_point,
            color="red",
            linestyle="--",
            alpha=0.8,
            label=f"Collapse point $\\approx$ {collapse_point:.2f}",
        )
    ax.set_xlabel("Conflict Density (Complexity)", fontsize=12)
    ax.set_ylabel("Fidelity / Coherence", fontsize=12)
    ax.set_title("Moral Phase Transition: Ethical Conflict → Spin Glass Frustration")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_compas_erh_bound(
    results: dict,
    title: str = "COMPAS: Adherence to Riemann Bound",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot COMPAS ERH analysis: Complexity (log) vs |E(x)| (log) with theoretical bound.

    X: Complexity (log scale).
    Y: Cumulative Error |E(x)| (log scale).
    Overlay: Theoretical bound y = C * x^0.5.
    Overlay: Actual COMPAS error curve.

    Parameters
    ----------
    results : dict
        From run_compas_erh_analysis: keys 'x', 'E_x', 'alpha', 'C'.
    """
    setup_paper_style()
    if "error" in results:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f"Error: {results['error']}", ha="center", va="center")
        return fig

    x = np.array(results["x"])
    E_x = np.array(results["E_x"])
    abs_E = np.abs(E_x)
    C = results.get("C", 1.0)

    fig, ax = plt.subplots(figsize=(10, 6))
    valid = (abs_E > 0) & (x > 1)
    if valid.sum() < 2:
        ax.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
        return fig

    ax.loglog(x[valid], abs_E[valid], "o-", label="COMPAS |E(x)|", linewidth=2, markersize=4)
    x_ref = np.linspace(max(1, x.min()), x.max(), 100)
    y_bound = C * np.sqrt(x_ref)
    ax.loglog(x_ref, y_bound, "--", color="gray", linewidth=2, label=r"$C \cdot x^{0.5}$ (ERH bound)")
    ax.set_xlabel("Complexity $x$ (log scale)", fontsize=12)
    ax.set_ylabel(r"$|E(x)|$ (log scale)", fontsize=12)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_universal_error_growth(
    error_comparison: dict,
    compas_results: dict,
    title: str = "Universal Error Growth Laws",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot |E(x)| vs. complexity x in log-log scale for BOTH simulated agents AND COMPAS
    on the same axes. When curves overlap, theory universality is visually proven.

    Parameters
    ----------
    error_comparison : dict
        From compare_error_distributions: judge name -> {x_values, E_x, analysis}.
    compas_results : dict
        From run_compas_erh_analysis: keys 'x', 'E_x', 'C'.
    """
    setup_paper_style()
    colors = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
    linestyles = ["-", "--", "-.", ":", "-", "--", "-."]

    fig, ax = plt.subplots(figsize=(10, 7))

    idx = 0
    for name, data in error_comparison.items():
        if "error" in data or "x_values" not in data:
            continue
        x_vals = np.array(data["x_values"])
        E_x = np.array(data["E_x"])
        abs_E = np.abs(E_x)
        valid = (abs_E > 0) & (x_vals > 1)
        if valid.sum() < 2:
            continue
        color = colors[idx % len(colors)]
        ls = linestyles[idx % len(linestyles)]
        ax.loglog(
            x_vals[valid], abs_E[valid],
            "o-", label=f"Simulated: {name}", linewidth=2, markersize=3,
            color=color, linestyle=ls,
        )
        idx += 1

    if "error" not in compas_results and "x" in compas_results:
        x = np.array(compas_results["x"])
        E_x = np.array(compas_results["E_x"])
        abs_E = np.abs(E_x)
        valid = (abs_E > 0) & (x > 1)
        if valid.sum() >= 2:
            ax.loglog(
                x[valid], abs_E[valid],
                "s-", label="COMPAS (real data)", linewidth=2.5, markersize=5,
                color="#e74c3c", linestyle="-",
            )
    # Always add ERH bound overlay
    C = compas_results.get("C", 1.0) if "error" not in compas_results else 1.0
    x_min = 1.0
    x_max = 100.0
    if "error" not in compas_results and "x" in compas_results:
        x_arr = np.array(compas_results["x"])
        x_min = max(1, float(np.min(x_arr)))
        x_max = float(np.max(x_arr))
    else:
        for data in error_comparison.values():
            if "error" not in data and "x_values" in data:
                x_arr = np.array(data["x_values"])
                x_max = max(x_max, float(np.max(x_arr)))
                break
    x_ref = np.linspace(x_min, x_max, 100)
    y_bound = C * np.sqrt(x_ref)
    ax.loglog(x_ref, y_bound, "--", color="gray", linewidth=2, label=r"$C \cdot x^{0.5}$ (ERH bound)")

    ax.set_xlabel("Complexity $x$ (log scale)", fontsize=12)
    ax.set_ylabel(r"$|E(x)|$ (log scale)", fontsize=12)
    ax.set_title(title)
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_alpha_comparison_bar(
    synthetic_results: dict,
    real_results: dict,
    title: str = r"$\alpha$ Comparison: Synthetic vs Real-World",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Bar chart comparing alpha of Radical, Conservative, COMPAS, Adult.
    Highlights COMPAS value (≈ -0.32).

    Parameters
    ----------
    synthetic_results : dict
        Keys like "Radical", "Conservative" with "alpha" value.
    real_results : dict
        Keys "compas", "adult" with "alpha" in nested dict.
    """
    setup_paper_style()
    labels = []
    values = []
    colors = []

    for name, data in synthetic_results.items():
        if "alpha" in data:
            labels.append(name)
            values.append(data["alpha"])
            colors.append("#3498db")

    compas_alpha = real_results.get("compas", {}).get("alpha")
    if compas_alpha is not None:
        labels.append("COMPAS")
        values.append(compas_alpha)
        colors.append("#e74c3c")

    adult_alpha = real_results.get("adult", {}).get("alpha")
    if adult_alpha is not None:
        labels.append("Adult")
        values.append(adult_alpha)
        colors.append("#2ecc71")

    if not labels:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, "No alpha data", ha="center", va="center")
        return fig

    fig, ax = plt.subplots(figsize=(10, 6))
    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, values, color=colors, edgecolor="black", linewidth=0.5)
    ax.axhline(y=0.5, color="red", linestyle="--", alpha=0.7, label="ERH threshold (0.5)")
    ax.axhline(y=-0.32, color="orange", linestyle=":", alpha=0.7, label="COMPAS ≈ -0.32")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylabel(r"Growth exponent $\alpha$")
    ax.set_title(title)
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_normalized_error_oscillation(
    x: np.ndarray,
    error: np.ndarray,
    confidence_interval: Optional[Tuple[float, float]] = None,
    title: str = r"Normalized Oscillation: $E(x)/\sqrt{x}$",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot E(x) / sqrt(x). Add horizontal lines for confidence intervals.

    Parameters
    ----------
    x : np.ndarray
        Complexity values.
    error : np.ndarray
        E(x) values.
    confidence_interval : tuple (low, high), optional
        Horizontal lines for confidence band.
    """
    setup_paper_style()
    sqrt_x = np.sqrt(np.maximum(x, 1e-6))
    ratio = np.where(sqrt_x > 1e-9, error / sqrt_x, 0.0)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, ratio, "o-", linewidth=2, markersize=4, label=r"$E(x)/\sqrt{x}$")
    ax.axhline(y=0, color="k", linestyle="-", linewidth=0.8, alpha=0.3)
    if confidence_interval is not None:
        low, high = confidence_interval
        ax.axhline(y=low, color="gray", linestyle=":", alpha=0.7)
        ax.axhline(y=high, color="gray", linestyle=":", alpha=0.7)
        ax.fill_between(x, low, high, alpha=0.1, color="gray")
    ax.set_xlabel("Complexity $x$", fontsize=12)
    ax.set_ylabel(r"$E(x) / \sqrt{x}$", fontsize=12)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_normalized_error_growth(
    x_values: np.ndarray,
    E_x: np.ndarray,
    title: str = "Riemann Evidence: $E(x)/\\sqrt{x}$ Normalized Oscillation",
    save_path: Optional[str] = None,
    show: bool = True,
    annotate_erh: bool = True,
) -> plt.Figure:
    """
    Plot E(x)/sqrt(x) vs x. If ERH holds, the curve should oscillate within bounds.

    X-axis: Complexity x.
    Y-axis: E(x) / sqrt(x).
    Bounded oscillation indicates ERH satisfaction.
    """
    setup_paper_style()
    sqrt_x = np.sqrt(np.maximum(x_values, 1e-6))
    ratio = np.where(sqrt_x > 1e-9, E_x / sqrt_x, 0.0)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_values, ratio, "o-", linewidth=2, markersize=4, label=r"$E(x)/\sqrt{x}$")
    ax.axhline(y=0, color="k", linestyle="-", linewidth=0.8, alpha=0.3)
    if annotate_erh and len(ratio) > 0:
        y_max = np.nanmax(np.abs(ratio)) if np.any(np.isfinite(ratio)) else 0
        if 0 < y_max < 5:
            mid_x = x_values[len(x_values) // 2]
            mid_y = np.median(ratio)
            text_y = max(y_max * 0.8, mid_y + 0.5) if y_max > 0 else 0.5
            ax.annotate(
                "ERH: bounded oscillation",
                xy=(mid_x, mid_y),
                xytext=(x_values[len(x_values) // 4], text_y),
                fontsize=10,
                color="green",
                bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.7),
            )
    ax.set_xlabel("Complexity $x$", fontsize=12)
    ax.set_ylabel(r"$E(x) / \sqrt{x}$", fontsize=12)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_quantum_phase_transition(
    h_values: np.ndarray,
    magnetization: np.ndarray,
    critical_h: Optional[float] = None,
    title: str = "Quantum Phase Transition: Magnetization vs Transverse Field",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot magnetization (consensus) vs transverse field strength h.

    X-axis: h (external pressure).
    Y-axis: Magnetization / consensus.
    Critical h_c marks有序→無序 transition.
    """
    setup_paper_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(h_values, magnetization, "o-", linewidth=2, label="Magnetization (Consensus)")
    if critical_h is not None:
        ax.axvline(
            x=critical_h,
            color="red",
            linestyle="--",
            alpha=0.8,
            label=f"Critical $h_c \\approx {critical_h:.2f}$",
        )
        ax.annotate("Ordered", xy=(h_values[0], magnetization[0]), fontsize=9, color="green")
        ax.annotate("Disordered", xy=(h_values[-1], magnetization[-1]), fontsize=9, color="red")
    ax.set_xlabel("Transverse Field $h$ (External Pressure)", fontsize=12)
    ax.set_ylabel("Magnetization (Consensus)", fontsize=12)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_prime_ladder(
    x_values: np.ndarray,
    Pi_x: np.ndarray,
    Li_x: Optional[np.ndarray] = None,
    title: str = "Ethical Prime Ladder: $\\Pi(x)$ vs $Li(x)$",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot step function Pi(x) with smooth Li(x) overlay.

    X-axis: Complexity x.
    Y-axis: Cumulative count.
    """
    setup_paper_style()
    if Li_x is None:
        x_safe = np.maximum(x_values, 1.1)
        Li_x = x_safe / np.log(x_safe)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.step(x_values, Pi_x, where="post", label=r"$\Pi(x)$ (Ethical Primes)", linewidth=2)
    ax.plot(x_values, Li_x, "--", label=r"$Li(x)$ (Smooth)", linewidth=2)
    ax.set_xlabel("Complexity $x$", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_von_neumann_entropy_over_time(
    time_steps: np.ndarray,
    entropy_values: np.ndarray,
    title: str = "Von Neumann Entropy (Echo-Chamber Indicator) Over Time",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot Von Neumann entropy over time. Low entropy = echo chamber; high = no consensus.
    """
    setup_paper_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_steps, entropy_values, "o-", linewidth=2)
    ax.set_xlabel("Time Step", fontsize=12)
    ax.set_ylabel("Von Neumann Entropy $S(\\rho)$", fontsize=12)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.annotate("Low: Echo chamber", xy=(time_steps[0], entropy_values[0]), fontsize=9, color="blue")
    ax.annotate("High: No consensus", xy=(time_steps[-1], entropy_values[-1]), fontsize=9, color="red")
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_social_tension_vs_time(
    time_steps: np.ndarray,
    social_tension: np.ndarray,
    title: str = "Social Tension (Energy) vs Time",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot social tension (quantum energy proxy for ethical conflict) over time.

    X-axis: Time step.
    Y-axis: Social Tension (Energy).

    Parameters
    ----------
    time_steps : np.ndarray
        Time step values.
    social_tension : np.ndarray
        Social tension (energy) values.
    title : str
        Plot title.
    save_path : Optional[str]
        Path to save figure.
    show : bool
        Whether to display.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_steps, social_tension, "o-", linewidth=2)
    ax.set_xlabel("Time Step", fontsize=12)
    ax.set_ylabel("Social Tension (Energy)", fontsize=12)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_phase_transition_error_vs_complexity(
    complexities: np.ndarray,
    error_rates: np.ndarray,
    title: str = "Error Rate vs Complexity (Phase Transition)",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Plot error rate vs complexity to visualize phase transition (error spike).

    X-axis: Complexity.
    Y-axis: Error Rate.

    Parameters
    ----------
    complexities : np.ndarray
        Complexity values.
    error_rates : np.ndarray
        Error rate at each complexity.
    title : str
        Plot title.
    save_path : Optional[str]
        Path to save figure.
    show : bool
        Whether to display.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(complexities, error_rates, "o-", linewidth=2)
    ax.set_xlabel("Complexity $x$", fontsize=12)
    ax.set_ylabel("Error Rate", fontsize=12)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_ethical_primes_map(
    primes: List,
    x_attr: str = "c",
    y_attr: str = "w",
    z_attr: Optional[str] = None,
    color_attr: Optional[str] = "delta",
    title: str = "Ethical Primes Map: Irreducible Dilemmas",
    save_path: Optional[str] = None,
    show: bool = True,
    use_3d: bool = False,
) -> plt.Figure:
    """
    Plot 3: Ethical Primes Map.

    2D or 3D scatter of "Irreducible Dilemmas" within the Action Space.
    x_attr: typically complexity (c).
    y_attr: typically importance (w).
    z_attr: optional third dimension (e.g. id, V).
    color_attr: typically delta (error magnitude).
    """
    if not primes:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "No ethical primes", ha="center", va="center", fontsize=14)
        return fig

    x_vals = [getattr(p, x_attr, p.c) for p in primes]
    y_vals = [getattr(p, y_attr, p.w) for p in primes]
    if color_attr:
        c_vals = [abs(getattr(p, color_attr, 0) or 0) for p in primes]
    else:
        c_vals = None

    use_3d = use_3d and z_attr and len(primes) >= 3 and Axes3D is not None
    if use_3d:
        z_vals = [getattr(p, z_attr, 0) for p in primes]
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection="3d")
        if c_vals:
            sc = ax.scatter(x_vals, y_vals, z_vals, c=c_vals, cmap="viridis", alpha=0.7, s=50)
            plt.colorbar(sc, ax=ax, label=f"|{color_attr}|")
        else:
            ax.scatter(x_vals, y_vals, z_vals, alpha=0.7, s=50)
        ax.set_xlabel(x_attr)
        ax.set_ylabel(y_attr)
        ax.set_zlabel(z_attr)
    else:
        fig, ax = plt.subplots(figsize=(10, 8))
        if c_vals:
            sc = ax.scatter(x_vals, y_vals, c=c_vals, cmap="viridis", alpha=0.7, s=50)
            plt.colorbar(sc, ax=ax, label=f"|{color_attr}|")
        else:
            ax.scatter(x_vals, y_vals, alpha=0.7, s=50)
        ax.set_xlabel(x_attr)
        ax.set_ylabel(y_attr)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def save_bloch_sphere_snapshot(
    state_vector: np.ndarray,
    step_number: int,
    save_dir: str,
) -> str:
    """
    Render the 3D ethical state of the society on the Bloch sphere.

    Each arrow represents an agent's orientation in Ethical Hilbert Space.
    Requires qiskit for plot_bloch_multivector.

    Parameters
    ----------
    state_vector : np.ndarray
        Quantum state vector (complex amplitudes).
    step_number : int
        Simulation step (used in filename).
    save_dir : str
        Directory to save the PNG.

    Returns
    -------
    str
        Path to saved file, or empty string if failed.
    """
    import os

    try:
        from qiskit.visualization import plot_bloch_multivector
    except ImportError:
        return ""

    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, f"bloch_state_step_{step_number:03d}.png")
    try:
        fig = plot_bloch_multivector(state_vector)
        if hasattr(fig, "savefig"):
            fig.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close("all")
        return filename
    except Exception:
        return ""

