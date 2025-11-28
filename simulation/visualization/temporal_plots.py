"""
Temporal Plots Module

This module provides visualization functions for temporal ERH analysis,
including 3D surface plots, time series animations, and anomaly marking.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
from typing import Optional, List, Dict, Tuple


def plot_3d_error_surface(
    E_xt: np.ndarray,
    x_values: np.ndarray,
    t_values: np.ndarray,
    save_path: Optional[str] = None,
    show: bool = True,
    title: str = "Error Evolution E(x,t)"
) -> plt.Figure:
    """
    Plot 3D surface of error evolution E(x,t).
    
    Parameters
    ----------
    E_xt : np.ndarray
        2D error array of shape (time_steps, X_max)
    x_values : np.ndarray
        Complexity values
    t_values : np.ndarray
        Time values
    save_path : Optional[str], default=None
        Path to save figure
    show : bool, default=True
        Whether to display figure
    title : str, default="Error Evolution E(x,t)"
        Plot title
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create meshgrid
    T, X = np.meshgrid(t_values, x_values, indexing='ij')
    
    # Plot surface
    surf = ax.plot_surface(X, T, E_xt, cmap='coolwarm', alpha=0.8, linewidth=0, antialiased=True)
    
    ax.set_xlabel('Complexity x', fontsize=12)
    ax.set_ylabel('Time t', fontsize=12)
    ax.set_zlabel('Error E(x,t)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Add colorbar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=20, label='Error Magnitude')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    
    return fig


def plot_temporal_evolution_animated(
    E_xt: np.ndarray,
    x_values: np.ndarray,
    t_values: np.ndarray,
    save_path: Optional[str] = None,
    interval: int = 200,
    anomalies: Optional[List[Dict]] = None
) -> animation.FuncAnimation:
    """
    Create animated plot of error evolution over time.
    
    Parameters
    ----------
    E_xt : np.ndarray
        2D error array
    x_values : np.ndarray
        Complexity values
    t_values : np.ndarray
        Time values
    save_path : Optional[str], default=None
        Path to save animation (requires writer like 'ffmpeg')
    interval : int, default=200
        Animation interval in milliseconds
    anomalies : Optional[List[Dict]], default=None
        List of anomalies to mark
        
    Returns
    -------
    animation.FuncAnimation
        Animation object
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Initialize plot
    line, = ax.plot([], [], 'b-', linewidth=2, label='E(x,t)')
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax.set_xlim(x_values[0], x_values[-1])
    ax.set_ylim(np.min(E_xt) * 1.1, np.max(E_xt) * 1.1)
    ax.set_xlabel('Complexity x', fontsize=12)
    ax.set_ylabel('Error E(x,t)', fontsize=12)
    ax.set_title('Temporal Error Evolution', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Anomaly markers
    anomaly_markers = []
    if anomalies:
        for anomaly in anomalies:
            marker, = ax.plot([], [], 'ro', markersize=10, alpha=0.7, label='Anomaly')
            anomaly_markers.append(marker)
    
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12,
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    def animate(frame):
        t_idx = frame
        if t_idx < E_xt.shape[0]:
            E_t = E_xt[t_idx, :]
            line.set_data(x_values, E_t)
            
            # Update anomaly markers
            if anomalies:
                for i, anomaly in enumerate(anomalies):
                    if anomaly['time'] == t_idx:
                        anomaly_markers[i].set_data([anomaly['complexity']], [anomaly['error_value']])
                    else:
                        anomaly_markers[i].set_data([], [])
            
            time_text.set_text(f'Time: t = {t_values[t_idx]:.1f}')
        
        return [line] + anomaly_markers + [time_text]
    
    anim = animation.FuncAnimation(
        fig, animate, frames=len(t_values), interval=interval, blit=True, repeat=True
    )
    
    if save_path:
        try:
            anim.save(save_path, writer='ffmpeg', fps=5)
        except Exception as e:
            print(f"Could not save animation: {e}")
            print("Animation will be displayed but not saved.")
    
    plt.tight_layout()
    return anim


def plot_anomaly_timeline(
    anomalies: List[Dict],
    E_xt: np.ndarray,
    x_values: np.ndarray,
    t_values: np.ndarray,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot timeline of anomalies with severity coloring.
    
    Parameters
    ----------
    anomalies : List[Dict]
        List of detected anomalies
    E_xt : np.ndarray
        Error array
    x_values : np.ndarray
        Complexity values
    t_values : np.ndarray
        Time values
    save_path : Optional[str], default=None
        Path to save figure
    show : bool, default=True
        Whether to display
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[2, 1])
    
    # Plot 1: Error surface with anomalies
    T, X = np.meshgrid(t_values, x_values, indexing='ij')
    im = ax1.contourf(X, T, E_xt, levels=20, cmap='coolwarm', alpha=0.8)
    ax1.contour(X, T, E_xt, levels=20, colors='black', alpha=0.3, linewidths=0.5)
    
    # Mark anomalies
    severity_colors = {
        'critical': 'red',
        'high': 'orange',
        'medium': 'yellow',
        'low': 'lightblue'
    }
    severity_sizes = {
        'critical': 200,
        'high': 150,
        'medium': 100,
        'low': 50
    }
    
    for anomaly in anomalies:
        color = severity_colors.get(anomaly.get('severity', 'low'), 'gray')
        size = severity_sizes.get(anomaly.get('severity', 'low'), 50)
        ax1.scatter(anomaly['complexity'], anomaly['time'], c=color, s=size,
                   edgecolors='black', linewidths=1.5, alpha=0.8, zorder=5)
    
    ax1.set_xlabel('Complexity x', fontsize=12)
    ax1.set_ylabel('Time t', fontsize=12)
    ax1.set_title('Error Evolution with Anomalies', fontsize=14, fontweight='bold')
    fig.colorbar(im, ax=ax1, label='Error E(x,t)')
    
    # Plot 2: Anomaly timeline
    if anomalies:
        anomaly_times = [a['time'] for a in anomalies]
        anomaly_severities = [a.get('severity', 'low') for a in anomalies]
        severity_numeric = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        severity_vals = [severity_numeric.get(s, 1) for s in anomaly_severities]
        
        ax2.scatter(anomaly_times, severity_vals, c=[severity_colors.get(s, 'gray') for s in anomaly_severities],
                   s=100, alpha=0.7, edgecolors='black', linewidths=1)
        ax2.set_xlabel('Time t', fontsize=12)
        ax2.set_ylabel('Severity', fontsize=12)
        ax2.set_yticks([1, 2, 3, 4])
        ax2.set_yticklabels(['Low', 'Medium', 'High', 'Critical'])
        ax2.set_title('Anomaly Timeline', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'No anomalies detected', ha='center', va='center',
                transform=ax2.transAxes, fontsize=12)
        ax2.set_xlabel('Time t', fontsize=12)
        ax2.set_ylabel('Severity', fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    
    return fig


def plot_temporal_trends_comparison(
    trends_by_complexity: Dict,
    selected_complexities: Optional[List[int]] = None,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot temporal trends for selected complexity levels.
    
    Parameters
    ----------
    trends_by_complexity : Dict
        Trends dictionary from analyze_temporal_trends
    selected_complexities : Optional[List[int]], default=None
        Specific complexities to plot. If None, plots all.
    save_path : Optional[str], default=None
        Path to save figure
    show : bool, default=True
        Whether to display
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    if selected_complexities is None:
        selected_complexities = sorted(trends_by_complexity.keys())
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    # Plot 1: Slopes
    complexities = []
    slopes = []
    for x in selected_complexities:
        if x in trends_by_complexity:
            complexities.append(x)
            slopes.append(trends_by_complexity[x]['slope'])
    
    axes[0].bar(complexities, slopes, color='steelblue', alpha=0.7, edgecolor='black')
    axes[0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
    axes[0].set_xlabel('Complexity x', fontsize=11)
    axes[0].set_ylabel('Trend Slope', fontsize=11)
    axes[0].set_title('Error Trend Slopes by Complexity', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Volatility
    volatilities = [trends_by_complexity[x]['volatility'] for x in complexities if x in trends_by_complexity]
    axes[1].bar(complexities[:len(volatilities)], volatilities, color='coral', alpha=0.7, edgecolor='black')
    axes[1].set_xlabel('Complexity x', fontsize=11)
    axes[1].set_ylabel('Volatility', fontsize=11)
    axes[1].set_title('Error Volatility by Complexity', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Mean errors
    mean_errors = [trends_by_complexity[x]['mean_error'] for x in complexities if x in trends_by_complexity]
    axes[2].bar(complexities[:len(mean_errors)], mean_errors, color='lightgreen', alpha=0.7, edgecolor='black')
    axes[2].set_xlabel('Complexity x', fontsize=11)
    axes[2].set_ylabel('Mean Error', fontsize=11)
    axes[2].set_title('Mean Error by Complexity', fontsize=12, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    
    # Plot 4: Max errors
    max_errors = [trends_by_complexity[x]['max_error'] for x in complexities if x in trends_by_complexity]
    axes[3].bar(complexities[:len(max_errors)], max_errors, color='gold', alpha=0.7, edgecolor='black')
    axes[3].set_xlabel('Complexity x', fontsize=11)
    axes[3].set_ylabel('Max Error', fontsize=11)
    axes[3].set_title('Max Error by Complexity', fontsize=12, fontweight='bold')
    axes[3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    
    return fig


def plot_forecast_comparison(
    E_xt: np.ndarray,
    forecast: Dict,
    x_values: np.ndarray,
    t_values: np.ndarray,
    selected_complexities: Optional[List[int]] = None,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot forecast comparison with historical data.
    
    Parameters
    ----------
    E_xt : np.ndarray
        Historical error array
    forecast : Dict
        Forecast results from forecast_error_growth
    x_values : np.ndarray
        Complexity values
    t_values : np.ndarray
        Historical time values
    selected_complexities : Optional[List[int]], default=None
        Specific complexities to plot
    save_path : Optional[str], default=None
        Path to save figure
    show : bool, default=True
        Whether to display
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    if selected_complexities is None:
        # Select a few representative complexities
        selected_complexities = [x_values[0], x_values[len(x_values)//4], 
                                x_values[len(x_values)//2], x_values[3*len(x_values)//4]]
    
    n_plots = len(selected_complexities)
    n_cols = 2
    n_rows = (n_plots + 1) // 2
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 4*n_rows))
    if n_plots == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    forecast_array = forecast['forecast']
    forecast_times = forecast['forecast_times']
    conf_intervals = forecast.get('confidence_intervals', {})
    
    for idx, x in enumerate(selected_complexities):
        if idx >= len(axes):
            break
        
        ax = axes[idx]
        x_idx = int(x) - 1
        if 0 <= x_idx < E_xt.shape[1]:
            # Historical data
            ax.plot(t_values, E_xt[:, x_idx], 'b-', linewidth=2, label='Historical', alpha=0.7)
            
            # Forecast
            ax.plot(forecast_times, forecast_array[:, x_idx], 'r--', linewidth=2, label='Forecast', alpha=0.8)
            
            # Confidence intervals
            if conf_intervals:
                lower = conf_intervals.get('lower', np.zeros_like(forecast_array))
                upper = conf_intervals.get('upper', np.zeros_like(forecast_array))
                ax.fill_between(forecast_times, lower[:, x_idx], upper[:, x_idx],
                               alpha=0.3, color='red', label='95% CI')
            
            ax.axvline(x=t_values[-1], color='gray', linestyle=':', alpha=0.5, label='Forecast start')
            ax.set_xlabel('Time t', fontsize=11)
            ax.set_ylabel('Error E(x,t)', fontsize=11)
            ax.set_title(f'Complexity x = {x}', fontsize=12, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for idx in range(len(selected_complexities), len(axes)):
        axes[idx].axis('off')
    
    plt.suptitle('Error Forecast Comparison', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    
    return fig

