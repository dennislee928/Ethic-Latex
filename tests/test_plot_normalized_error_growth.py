"""Tests for plot_normalized_error_growth."""

import numpy as np
import pytest

try:
    from simulation.visualization.plots import plot_normalized_error_growth
except ImportError:
    plot_normalized_error_growth = None


@pytest.mark.skipif(plot_normalized_error_growth is None, reason="plots module unavailable")
def test_plot_normalized_error_growth_returns_figure():
    """plot_normalized_error_growth returns a matplotlib Figure."""
    x = np.arange(2, 51)
    E_x = 0.5 * np.sqrt(x) * np.sin(np.log(x))
    fig = plot_normalized_error_growth(x, E_x, show=False)
    assert fig is not None
    assert hasattr(fig, "savefig")


@pytest.mark.skipif(plot_normalized_error_growth is None, reason="plots module unavailable")
def test_plot_normalized_error_growth_save(tmp_path):
    """plot_normalized_error_growth can save to file."""
    x = np.arange(2, 21)
    E_x = np.sqrt(x) * 0.1
    save_path = tmp_path / "normalized.pdf"
    fig = plot_normalized_error_growth(x, E_x, save_path=str(save_path), show=False)
    assert save_path.exists()
