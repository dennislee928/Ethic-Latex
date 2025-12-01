"""
Unit tests for agent framework.
"""

import sys
import os
from pathlib import Path

simulation_dir = Path(__file__).parent.parent / "simulation"
sys.path.insert(0, str(simulation_dir))

import numpy as np
import pytest
from core.agent import EthicalAgent, AgentPopulation, SimpleEthicalAgent
from core.judgement_system import BiasedJudge
from core.action_space import Action, generate_world


class TestEthicalAgent:
    """Test EthicalAgent class."""
    
    def test_agent_creation(self):
        """Test agent creation."""
        judge = BiasedJudge(bias_strength=0.2)
        agent = SimpleEthicalAgent(agent_id=0, judge=judge)
        
        assert agent.agent_id == 0
        assert agent.judge == judge
        assert agent.error_rate == 0.0
    
    def test_judge_action(self):
        """Test action judgment."""
        judge = BiasedJudge(bias_strength=0.2)
        agent = SimpleEthicalAgent(agent_id=0, judge=judge)
        
        action = Action(id=0, c=50, V=0.5, w=1.0)
        judgment = agent.judge_action(action, tau=0.3)
        
        assert action.J is not None
        assert action.delta is not None
        assert action.mistake_flag in [0, 1]
        assert agent.state['total_judgments'] == 1
    
    def test_update_from_interaction(self):
        """Test agent interaction."""
        judge1 = BiasedJudge(bias_strength=0.1)
        judge2 = BiasedJudge(bias_strength=0.3)
        
        agent1 = SimpleEthicalAgent(agent_id=0, judge=judge1, initial_error_rate=0.1)
        agent2 = SimpleEthicalAgent(agent_id=1, judge=judge2, initial_error_rate=0.2)
        
        initial_error1 = agent1.error_rate
        agent1.update_from_interaction(agent2, influence_strength=0.5)
        
        # Error rate should move toward agent2's rate
        assert agent1.error_rate != initial_error1
        assert len(agent1.interaction_history) == 1


class TestAgentPopulation:
    """Test AgentPopulation class."""
    
    def test_population_creation(self):
        """Test population creation."""
        def judge_factory(i):
            return BiasedJudge(bias_strength=0.1 + 0.1 * i / 10)
        
        population = AgentPopulation()
        population.create_population(10, judge_factory, SimpleEthicalAgent)
        
        assert len(population) == 10
        assert len(population.agents) == 10
    
    def test_evaluate_actions(self):
        """Test batch action evaluation."""
        def judge_factory(i):
            return BiasedJudge(bias_strength=0.1)
        
        population = AgentPopulation()
        population.create_population(3, judge_factory, SimpleEthicalAgent)
        
        actions = generate_world(num_actions=50, random_seed=42)
        results = population.evaluate_actions(actions, tau=0.3)
        
        assert len(results) == 3
        for agent_id, evaluated_actions in results.items():
            assert len(evaluated_actions) == 50
            assert all(a.J is not None for a in evaluated_actions)
    
    def test_population_statistics(self):
        """Test population statistics."""
        def judge_factory(i):
            return BiasedJudge(bias_strength=0.1)
        
        population = AgentPopulation()
        population.create_population(5, judge_factory, SimpleEthicalAgent)
        
        stats = population.get_population_statistics()
        
        assert stats['num_agents'] == 5
        assert 'mean_error_rate' in stats
        assert 'std_error_rate' in stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


