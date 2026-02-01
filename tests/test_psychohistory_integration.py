"""
Integration tests for psychohistory components.

Uses conftest.py for pythonpath setup; no sys.path.insert hacks.
"""

import numpy as np
import pytest

try:
    from simulation.core.action_space import generate_world
    from simulation.core.judgement_system import BiasedJudge
    from simulation.core.temporal_erh import track_error_evolution
    from simulation.core.agent import AgentPopulation, SimpleEthicalAgent
    from simulation.core.social_network import SocialNetwork
    from simulation.core.abm_simulator import ABMSimulator
    from simulation.analysis.opinion_dynamics import degroot_model
    from simulation.analysis.temporal_analysis import (
        analyze_temporal_trends,
        detect_anomalies,
    )
except ImportError as e:
    pytest.skip(f"Failed to import required modules: {e}", allow_module_level=True)


class TestPsychohistoryIntegration:
    """Test integration of psychohistory components."""
    
    def test_temporal_with_abm(self):
        """Test temporal ERH with ABM."""
        def judge_factory(i):
            return BiasedJudge(bias_strength=0.1)
        
        abm = ABMSimulator(
            num_agents=5,
            judge_factory=judge_factory,
            enable_meta_monitor=True
        )
        
        results = abm.run_simulation(
            num_time_steps=3,
            actions_per_step=100,
            tau=0.3,
            X_max=50,
            track_erh=True
        )
        
        assert 'erh_history' in results
        assert len(results['erh_history']) == 3
    
    def test_network_with_opinion_dynamics(self):
        """Test network with opinion dynamics."""
        agents = []
        for i in range(10):
            judge = BiasedJudge(bias_strength=0.1)
            agent = SimpleEthicalAgent(agent_id=i, judge=judge)
            agent.judgment_tendency = np.random.uniform(-0.5, 0.5)
            agents.append(agent)
        
        network = SocialNetwork(agents=agents, topology='small_world', n_nodes=10)
        
        result = degroot_model(agents, network, max_iterations=10)
        
        assert 'converged' in result
        assert 'final_opinions' in result
    
    def test_temporal_analysis(self):
        """Test temporal analysis functions."""
        # Generate temporal data
        actions_history = []
        judge = BiasedJudge(bias_strength=0.2)
        
        for t in range(5):
            actions = generate_world(num_actions=200, random_seed=42 + t)
            actions_history.append(actions)
        
        temporal_results = track_error_evolution(
            actions_history, judge, tau=0.3, time_steps=5, X_max=50
        )
        
        E_xt = temporal_results['E_xt']
        x_values = np.arange(1, 51)
        
        # Analyze trends
        trends = analyze_temporal_trends(E_xt, time_steps=5, x_values=x_values)
        
        assert 'overall_trend' in trends
        assert 'volatility' in trends
        
        # Detect anomalies
        anomalies = detect_anomalies(E_xt, method='statistical', X_max=50)
        
        assert isinstance(anomalies, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

