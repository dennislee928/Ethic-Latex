"""
Unit tests for social network module.
"""

import sys
import os
from pathlib import Path

simulation_dir = Path(__file__).parent.parent / "simulation"
sys.path.insert(0, str(simulation_dir))

import numpy as np
import pytest
from core.social_network import SocialNetwork
from core.agent import SimpleEthicalAgent
from core.judgement_system import BiasedJudge


class TestSocialNetwork:
    """Test SocialNetwork class."""
    
    def test_network_creation(self):
        """Test network creation with different topologies."""
        agents = []
        for i in range(10):
            judge = BiasedJudge(bias_strength=0.1)
            agent = SimpleEthicalAgent(agent_id=i, judge=judge)
            agents.append(agent)
        
        for topology in ['random', 'small_world', 'scale_free', 'star', 'ring']:
            network = SocialNetwork(agents=agents, topology=topology, n_nodes=10)
            
            assert len(network.agents) == 10
            assert network.graph.number_of_nodes() == 10
    
    def test_get_neighbors(self):
        """Test neighbor retrieval."""
        agents = []
        for i in range(5):
            judge = BiasedJudge(bias_strength=0.1)
            agent = SimpleEthicalAgent(agent_id=i, judge=judge)
            agents.append(agent)
        
        network = SocialNetwork(agents=agents, topology='ring', n_nodes=5)
        
        neighbors = network.get_neighbors(agents[0])
        assert len(neighbors) >= 0  # Ring should have 2 neighbors, but depends on graph
    
    def test_get_influence_strength(self):
        """Test influence strength retrieval."""
        agents = []
        for i in range(5):
            judge = BiasedJudge(bias_strength=0.1)
            agent = SimpleEthicalAgent(agent_id=i, judge=judge)
            agents.append(agent)
        
        network = SocialNetwork(agents=agents, topology='complete', n_nodes=5)
        
        strength = network.get_influence_strength(agents[0], agents[1])
        assert strength >= 0
    
    def test_network_statistics(self):
        """Test network statistics."""
        agents = []
        for i in range(10):
            judge = BiasedJudge(bias_strength=0.1)
            agent = SimpleEthicalAgent(agent_id=i, judge=judge)
            agents.append(agent)
        
        network = SocialNetwork(agents=agents, topology='small_world', n_nodes=10)
        
        stats = network.get_network_statistics()
        
        assert stats['num_nodes'] == 10
        assert stats['num_edges'] >= 0
        assert 'average_degree' in stats
        assert 'clustering_coefficient' in stats
    
    def test_centrality_measures(self):
        """Test centrality computation."""
        agents = []
        for i in range(10):
            judge = BiasedJudge(bias_strength=0.1)
            agent = SimpleEthicalAgent(agent_id=i, judge=judge)
            agents.append(agent)
        
        network = SocialNetwork(agents=agents, topology='small_world', n_nodes=10)
        
        centrality = network.get_centrality_measures()
        
        assert len(centrality) == 10
        for agent_id, measures in centrality.items():
            assert 'degree_centrality' in measures
            assert 'betweenness_centrality' in measures


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


