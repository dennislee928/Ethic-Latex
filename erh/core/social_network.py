"""
Social Network Module

This module implements social network structures for modeling agent interactions
in psychohistory-style simulations. Networks represent information and influence
propagation between AI judgment agents.
"""

import numpy as np
import networkx as nx
from typing import List, Optional, Dict, Tuple, Literal
from .agent import EthicalAgent


class SocialNetwork:
    """
    Social network for agent interactions.
    
    Nodes represent AI judgment agents, edges represent information/influence
    propagation. Supports multiple network topologies.
    
    Attributes
    ----------
    graph : nx.Graph
        NetworkX graph representing the network
    agents : List[EthicalAgent]
        List of agents in the network
    agent_to_node : Dict[int, int]
        Mapping from agent_id to node index
    """
    
    def __init__(
        self,
        agents: Optional[List[EthicalAgent]] = None,
        topology: Literal['random', 'small_world', 'scale_free', 'star', 'ring', 'complete'] = 'random',
        **topology_params
    ):
        """
        Initialize social network.
        
        Parameters
        ----------
        agents : Optional[List[EthicalAgent]], default=None
            List of agents. If None, network starts empty.
        topology : str, default='random'
            Network topology type
        **topology_params
            Additional parameters for topology generation:
            - For 'random': n_nodes, p (connection probability)
            - For 'small_world': n_nodes, k (neighbors), p (rewiring probability)
            - For 'scale_free': n_nodes, m (edges per new node)
            - For 'star': n_nodes (central node + n_nodes-1 leaves)
            - For 'ring': n_nodes
            - For 'complete': n_nodes
        """
        self.graph = nx.Graph()
        self.agents = agents if agents is not None else []
        self.agent_to_node = {}
        
        if len(self.agents) > 0:
            self._build_network(topology, **topology_params)
    
    def _build_network(
        self,
        topology: str,
        n_nodes: Optional[int] = None,
        **params
    ):
        """
        Build network with specified topology.
        
        Parameters
        ----------
        topology : str
            Topology type
        n_nodes : Optional[int], default=None
            Number of nodes. If None, uses number of agents.
        **params
            Topology-specific parameters
        """
        if n_nodes is None:
            n_nodes = len(self.agents)
        
        # Generate network topology
        if topology == 'random':
            p = params.get('p', 0.1)
            self.graph = nx.erdos_renyi_graph(n_nodes, p)
            
        elif topology == 'small_world':
            k = params.get('k', 4)
            p = params.get('p', 0.3)
            self.graph = nx.watts_strogatz_graph(n_nodes, k, p)
            
        elif topology == 'scale_free':
            m = params.get('m', 2)
            self.graph = nx.barabasi_albert_graph(n_nodes, m)
            
        elif topology == 'star':
            # Star: one central node connected to all others
            self.graph = nx.star_graph(n_nodes - 1)
            
        elif topology == 'ring':
            self.graph = nx.cycle_graph(n_nodes)
            
        elif topology == 'complete':
            self.graph = nx.complete_graph(n_nodes)
            
        else:
            raise ValueError(f"Unknown topology: {topology}")
        
        # Map agents to nodes
        self.agent_to_node = {}
        node_to_agent = {}
        for i, agent in enumerate(self.agents[:n_nodes]):
            node_id = i
            self.agent_to_node[agent.agent_id] = node_id
            node_to_agent[node_id] = agent
        
        # Add node attributes
        for node_id in self.graph.nodes():
            if node_id in node_to_agent:
                agent = node_to_agent[node_id]
                self.graph.nodes[node_id]['agent_id'] = agent.agent_id
                self.graph.nodes[node_id]['error_rate'] = agent.error_rate
                self.graph.nodes[node_id]['tendency'] = agent.judgment_tendency
    
    def add_agent(self, agent: EthicalAgent):
        """
        Add an agent to the network.
        
        Parameters
        ----------
        agent : EthicalAgent
            Agent to add
        """
        self.agents.append(agent)
        node_id = len(self.agents) - 1
        self.agent_to_node[agent.agent_id] = node_id
        self.graph.add_node(node_id, agent_id=agent.agent_id)
    
    def add_edge(self, agent1: EthicalAgent, agent2: EthicalAgent, weight: float = 1.0):
        """
        Add an edge between two agents.
        
        Parameters
        ----------
        agent1 : EthicalAgent
            First agent
        agent2 : EthicalAgent
            Second agent
        weight : float, default=1.0
            Edge weight (influence strength)
        """
        if agent1.agent_id in self.agent_to_node and agent2.agent_id in self.agent_to_node:
            node1 = self.agent_to_node[agent1.agent_id]
            node2 = self.agent_to_node[agent2.agent_id]
            self.graph.add_edge(node1, node2, weight=weight)
    
    def get_neighbors(self, agent: EthicalAgent) -> List[EthicalAgent]:
        """
        Get neighboring agents (connected in network).
        
        Parameters
        ----------
        agent : EthicalAgent
            Agent to find neighbors for
            
        Returns
        -------
        List[EthicalAgent]
            List of neighboring agents
        """
        if agent.agent_id not in self.agent_to_node:
            return []
        
        node_id = self.agent_to_node[agent.agent_id]
        neighbor_nodes = list(self.graph.neighbors(node_id))
        
        neighbors = []
        for node_id in neighbor_nodes:
            agent_id = self.graph.nodes[node_id].get('agent_id')
            if agent_id is not None:
                for a in self.agents:
                    if a.agent_id == agent_id:
                        neighbors.append(a)
                        break
        
        return neighbors
    
    def get_influence_strength(self, agent1: EthicalAgent, agent2: EthicalAgent) -> float:
        """
        Get influence strength between two agents.
        
        Parameters
        ----------
        agent1 : EthicalAgent
            First agent
        agent2 : EthicalAgent
            Second agent
            
        Returns
        -------
        float
            Influence strength (edge weight, or 0 if not connected)
        """
        if agent1.agent_id not in self.agent_to_node or agent2.agent_id not in self.agent_to_node:
            return 0.0
        
        node1 = self.agent_to_node[agent1.agent_id]
        node2 = self.agent_to_node[agent2.agent_id]
        
        if self.graph.has_edge(node1, node2):
            return self.graph[node1][node2].get('weight', 1.0)
        return 0.0
    
    def update_node_attributes(self):
        """
        Update node attributes from current agent states.
        """
        for agent in self.agents:
            if agent.agent_id in self.agent_to_node:
                node_id = self.agent_to_node[agent.agent_id]
                self.graph.nodes[node_id]['error_rate'] = agent.error_rate
                self.graph.nodes[node_id]['tendency'] = agent.judgment_tendency
    
    def get_network_statistics(self) -> Dict:
        """
        Get network statistics.
        
        Returns
        -------
        Dict
            Network statistics including:
            - num_nodes, num_edges
            - average_degree
            - clustering_coefficient
            - average_path_length
            - density
        """
        if len(self.graph.nodes()) == 0:
            return {
                'num_nodes': 0,
                'num_edges': 0,
                'average_degree': 0.0,
                'clustering_coefficient': 0.0,
                'average_path_length': 0.0,
                'density': 0.0
            }
        
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        
        # Average degree
        degrees = dict(self.graph.degree())
        avg_degree = np.mean(list(degrees.values())) if degrees else 0.0
        
        # Clustering coefficient
        clustering = nx.average_clustering(self.graph)
        
        # Average path length (only for connected graphs)
        if nx.is_connected(self.graph):
            avg_path_length = nx.average_shortest_path_length(self.graph)
        else:
            # For disconnected graphs, compute for each component
            components = list(nx.connected_components(self.graph))
            path_lengths = []
            for comp in components:
                subgraph = self.graph.subgraph(comp)
                if len(comp) > 1:
                    path_lengths.append(nx.average_shortest_path_length(subgraph))
            avg_path_length = np.mean(path_lengths) if path_lengths else 0.0
        
        # Density
        max_edges = num_nodes * (num_nodes - 1) / 2
        density = num_edges / max_edges if max_edges > 0 else 0.0
        
        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'average_degree': avg_degree,
            'clustering_coefficient': clustering,
            'average_path_length': avg_path_length,
            'density': density
        }
    
    def get_centrality_measures(self) -> Dict[int, Dict]:
        """
        Compute centrality measures for each agent.
        
        Returns
        -------
        Dict[int, Dict]
            Dictionary mapping agent_id to centrality measures:
            - degree_centrality
            - betweenness_centrality
            - closeness_centrality
            - eigenvector_centrality
        """
        if len(self.graph.nodes()) == 0:
            return {}
        
        degree_cent = nx.degree_centrality(self.graph)
        betweenness_cent = nx.betweenness_centrality(self.graph)
        closeness_cent = nx.closeness_centrality(self.graph)
        
        try:
            eigenvector_cent = nx.eigenvector_centrality(self.graph, max_iter=100)
        except:
            eigenvector_cent = {node: 0.0 for node in self.graph.nodes()}
        
        centrality_by_agent = {}
        for agent in self.agents:
            if agent.agent_id in self.agent_to_node:
                node_id = self.agent_to_node[agent.agent_id]
                centrality_by_agent[agent.agent_id] = {
                    'degree_centrality': degree_cent.get(node_id, 0.0),
                    'betweenness_centrality': betweenness_cent.get(node_id, 0.0),
                    'closeness_centrality': closeness_cent.get(node_id, 0.0),
                    'eigenvector_centrality': eigenvector_cent.get(node_id, 0.0)
                }
        
        return centrality_by_agent
    
    def detect_communities(self) -> Dict[int, int]:
        """
        Detect communities (clusters) in the network.
        
        Returns
        -------
        Dict[int, int]
            Mapping from agent_id to community_id
        """
        if len(self.graph.nodes()) == 0:
            return {}
        
        try:
            communities = nx.community.greedy_modularity_communities(self.graph)
        except:
            # Fallback: each node is its own community
            communities = [{node} for node in self.graph.nodes()]
        
        agent_to_community = {}
        for comm_id, comm in enumerate(communities):
            for node_id in comm:
                agent_id = self.graph.nodes[node_id].get('agent_id')
                if agent_id is not None:
                    agent_to_community[agent_id] = comm_id
        
        return agent_to_community
    
    def visualize_network(self, save_path: Optional[str] = None):
        """
        Visualize the network (requires matplotlib).
        
        Parameters
        ----------
        save_path : Optional[str], default=None
            Path to save figure. If None, displays interactively.
        """
        try:
            import matplotlib.pyplot as plt
            
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
            
            plt.figure(figsize=(12, 8))
            nx.draw_networkx_nodes(self.graph, pos, node_color='lightblue', node_size=500)
            nx.draw_networkx_edges(self.graph, pos, alpha=0.5)
            nx.draw_networkx_labels(self.graph, pos, font_size=8)
            
            plt.title('Social Network Topology')
            plt.axis('off')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            else:
                plt.show()
        except ImportError:
            print("matplotlib not available for visualization")


