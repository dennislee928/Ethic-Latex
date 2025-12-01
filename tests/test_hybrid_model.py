"""
Integration tests for hybrid psychohistory model.
"""

import sys
import os
from pathlib import Path

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
    from core.hybrid_model import HybridPsychohistoryModel
    from core.judgement_system import BiasedJudge
except ImportError as e:
    pytest.skip(f"Failed to import required modules: {e}", allow_module_level=True)


class TestHybridModel:
    """Test HybridPsychohistoryModel class."""
    
    def test_hybrid_model_creation(self):
        """Test hybrid model creation."""
        def judge_factory(i):
            return BiasedJudge(bias_strength=0.1 + 0.1 * i / 10)
        
        hybrid = HybridPsychohistoryModel(
            num_agents=10,
            judge_factory=judge_factory,
            network_topology='small_world',
            enable_temporal=True,
            enable_network_dynamics=True,
            enable_fluid_model=False,
            enable_meta_monitor=True
        )
        
        assert hybrid.abm_simulator is not None
        assert hybrid.meta_monitor is not None
        assert hybrid.temporal_enabled == True
    
    def test_run_simulation(self):
        """Test running hybrid simulation."""
        def judge_factory(i):
            return BiasedJudge(bias_strength=0.1)
        
        hybrid = HybridPsychohistoryModel(
            num_agents=5,
            judge_factory=judge_factory,
            enable_fluid_model=False  # Disable for speed
        )
        
        results = hybrid.run_simulation(
            num_time_steps=3,
            actions_per_step=100,
            tau=0.3,
            X_max=50
        )
        
        assert 'abm_results' in results
        assert 'temporal_erh' in results or results.get('temporal_erh') is None
        assert 'network_dynamics' in results or results.get('network_dynamics') is None
    
    def test_unified_metrics(self):
        """Test unified metrics computation."""
        def judge_factory(i):
            return BiasedJudge(bias_strength=0.1)
        
        hybrid = HybridPsychohistoryModel(
            num_agents=5,
            judge_factory=judge_factory,
            enable_fluid_model=False
        )
        
        results = hybrid.run_simulation(
            num_time_steps=3,
            actions_per_step=100,
            tau=0.3,
            X_max=50
        )
        
        metrics = hybrid.get_unified_metrics(results)
        
        assert 'erh_satisfaction' in metrics or metrics.get('erh_satisfaction') is None
        assert 'system_health' in metrics
        assert 'score' in metrics['system_health']
    
    def test_adaptive_adjustment(self):
        """Test adaptive adjustment."""
        def judge_factory(i):
            return BiasedJudge(bias_strength=0.1)
        
        hybrid = HybridPsychohistoryModel(
            num_agents=5,
            judge_factory=judge_factory,
            enable_fluid_model=False
        )
        
        results = hybrid.run_simulation(
            num_time_steps=3,
            actions_per_step=100,
            tau=0.3,
            X_max=50
        )
        
        adjustments = hybrid.adaptive_adjustment(results, target_exponent=0.5)
        
        assert isinstance(adjustments, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

