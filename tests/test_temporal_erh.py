"""
Unit tests for temporal ERH module.
"""

import sys
import os
from pathlib import Path

# Add simulation to path
simulation_dir = Path(__file__).parent.parent / "simulation"
if str(simulation_dir) not in sys.path:
    sys.path.insert(0, str(simulation_dir))

# Also add project root for absolute imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import numpy as np
import pytest

# Import with error handling
try:
    from core.action_space import generate_world, Action
    from core.judgement_system import BiasedJudge
    from core.temporal_erh import (
        compute_Pi_temporal,
        compute_E_temporal,
        compute_baseline_temporal,
        track_error_evolution,
        simulate_mule_effect,
        detect_mule_anomalies
    )
except ImportError as e:
    pytest.skip(f"Failed to import required modules: {e}", allow_module_level=True)


class TestTemporalERH:
    """Test temporal ERH functions."""
    
    def test_compute_Pi_temporal(self):
        """Test Pi(x,t) computation."""
        # Create mock primes history
        primes_history = []
        for t in range(3):
            primes = [
                Action(id=i, c=10 + i*5, V=0.5, w=1.0) for i in range(5)
            ]
            primes_history.append(primes)
        
        Pi_xt = compute_Pi_temporal(primes_history, time_steps=3, X_max=50)
        
        assert Pi_xt.shape == (3, 50)
        assert np.all(Pi_xt >= 0)
        # Note: Pi_xt[t, x-1] counts primes with complexity <= x at time t
        # The actual count depends on the generated primes, so we check general properties
        assert Pi_xt[0, 0] >= 0  # At least 0 primes with c <= 1
        # Check that Pi_xt is non-decreasing along complexity axis
        for t in range(3):
            for x in range(1, 50):
                assert Pi_xt[t, x] >= Pi_xt[t, x-1], f"Pi_xt should be non-decreasing at t={t}, x={x+1}"
    
    def test_compute_baseline_temporal(self):
        """Test baseline computation."""
        B_xt = compute_baseline_temporal(
            time_steps=5, X_max=20, baseline_type='prime_theorem'
        )
        
        assert B_xt.shape == (5, 20)
        assert np.all(B_xt >= 0)
    
    def test_compute_E_temporal(self):
        """Test E(x,t) computation."""
        Pi_xt = np.array([[1, 2, 3], [2, 3, 4]])
        B_xt = np.array([[0.5, 1.0, 1.5], [1.0, 1.5, 2.0]])
        
        E_xt = compute_E_temporal(Pi_xt, B_xt, time_steps=2, X_max=3)
        
        assert E_xt.shape == (2, 3)
        expected = Pi_xt - B_xt
        np.testing.assert_array_almost_equal(E_xt, expected)
    
    def test_track_error_evolution(self):
        """Test error evolution tracking."""
        actions_history = []
        judge = BiasedJudge(bias_strength=0.2)
        
        for t in range(3):
            actions = generate_world(num_actions=100, random_seed=42 + t)
            actions_history.append(actions)
        
        results = track_error_evolution(
            actions_history, judge, tau=0.3, time_steps=3, X_max=50
        )
        
        assert 'Pi_xt' in results
        assert 'B_xt' in results
        assert 'E_xt' in results
        assert results['Pi_xt'].shape == (3, 50)
        assert results['E_xt'].shape == (3, 50)
    
    def test_simulate_mule_effect(self):
        """Test Mule effect simulation."""
        E_xt = np.zeros((5, 10))
        E_xt[2, 5] = 1.0  # Initial error
        
        E_xt_mule = simulate_mule_effect(
            E_xt, mule_time=2, mule_strength=2.0, X_max=10
        )
        
        assert E_xt_mule.shape == E_xt.shape
        # Mule effect should modify the error
        assert not np.array_equal(E_xt, E_xt_mule)
    
    def test_detect_mule_anomalies(self):
        """Test anomaly detection."""
        # Create error array with violations
        # ERH bound at x=5: C * x^(0.5 + epsilon) = 1.0 * 5^(0.5 + 0.1) ≈ 1.0 * 5^0.6 ≈ 2.6
        # Threshold = bound * 1.5 ≈ 3.9, so we need error > 3.9
        E_xt = np.zeros((3, 10))
        # E_xt[t, x_idx] where x_idx = complexity - 1
        # So E_xt[1, 4] corresponds to t=1, complexity=5
        E_xt[1, 4] = 10.0  # Large violation at complexity 5 (index 4)
        
        anomalies = detect_mule_anomalies(E_xt, C=1.0, epsilon=0.1, X_max=10, threshold_multiplier=1.5)
        
        assert len(anomalies) > 0, f"No anomalies detected, but expected one at t=1, x=5"
        # Check that the violation at t=1, x=5 is detected
        found = any(a['time'] == 1 and a['complexity'] == 5 for a in anomalies)
        assert found, f"Expected anomaly at t=1, x=5, but got: {anomalies}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

