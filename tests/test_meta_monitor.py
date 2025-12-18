"""
Unit tests for meta-monitor module.
"""

import sys
import os
from pathlib import Path

simulation_dir = Path(__file__).parent.parent / "simulation"
sys.path.insert(0, str(simulation_dir))

import numpy as np
import pytest
from core.meta_monitor import MetaMonitor, ERHParameters, CorrectionAction


class TestMetaMonitor:
    """Test MetaMonitor class."""
    
    def test_monitor_creation(self):
        """Test monitor creation."""
        monitor = MetaMonitor()
        
        assert monitor.erh_params is not None
        assert monitor.monitoring_active == True
        assert len(monitor.violation_history) == 0
    
    def test_monitor_detection(self):
        """Test violation detection."""
        monitor = MetaMonitor(violation_threshold=1.5)
        
        # Create error array with violation
        E_xt = np.zeros((3, 10))
        E_xt[1, 5] = 10.0  # Large violation
        
        result = monitor.monitor(E_xt, time_step=1, X_max=10)
        
        assert len(result['violations_detected']) > 0
    
    def test_adaptive_parameters(self):
        """Test adaptive parameter adjustment."""
        monitor = MetaMonitor()
        
        # Create error history (2D array: time_steps x X_max)
        E_xt_history = []
        for t in range(5):
            E_xt = np.random.rand(1, 10) * 0.5  # Shape: (1, 10) for each time step
            E_xt_history.append(E_xt)
        
        new_params = monitor.adaptive_erh_parameters(E_xt_history, target_exponent=0.5)
        
        assert new_params is not None
        assert new_params.C > 0
        assert new_params.epsilon >= 0
    
    def test_monitoring_summary(self):
        """Test monitoring summary."""
        monitor = MetaMonitor()
        
        # Simulate some violations
        E_xt = np.zeros((3, 10))
        E_xt[1, 5] = 10.0
        monitor.monitor(E_xt, time_step=1, X_max=10)
        
        summary = monitor.get_monitoring_summary()
        
        assert 'total_violations' in summary
        assert 'corrections_applied' in summary
        assert 'current_params' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
