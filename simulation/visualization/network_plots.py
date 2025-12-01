"""
Network Plots Module

This module provides visualization functions for social network analysis,
including network topology visualization, opinion propagation animations,
and error density distribution on networks.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import networkx as nx
from typing import Optional, List, Dict, Tuple
from ..core.social_network import SocialNetwork
from ..core.agent import EthicalAgent


def plot_network_topology(
    network: SocialNetwork,
    node_color_attribute: str = 'error_rate',
    node_size_attribute: str = 'degree',
    save_path: Optional[str] = None,
    show: bool = True,
    title: str = "Social Network Topology"
) -> plt.Figure:
    """
    Visualize network topology with node attributes.
    
    Parameters
    ----------
    network : SocialNetwork
        Social network to visualize
    node_color_attribute : str, default='error_rate'
        Node attribute for coloring: 'error_rate', 'tendency', 'centrality'
    node_size_attribute : str, default='degree'
        Node attribute for sizing: 'degree', 'error_rate', 'centrality'
    save_path : Optional[str], default=None
        Path to save figure
    show : bool, default=True
        Whether to display
    title : str, default="Social Network Topology"
        Plot title
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    if len(network.graph.nodes()) == 0:
        print("Network is empty, cannot visualize")
        return None
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Layout
    pos = nx.spring_layout(network.graph, k=1, iterations=50, seed=42)
    
    # Node colors
    node_colors = []
    if node_color_attribute == 'error_rate':
        for node_id in network.graph.nodes():
            agent_id = network.graph.nodes[node_id].get('agent_id')
            if agent_id is not None:
                agent = next((a for a in network.agents if a.agent_id == agent_id), None)
                if agent:
                    node_colors.append(agent.error_rate)
                else:
                    node_colors.append(0.0)
            else:
                node_colors.append(0.0)
    elif node_color_attribute == 'tendency':
        for node_id in network.graph.nodes():
            agent_id = network.graph.nodes[node_id].get('agent_id')
            if agent_id is not None:
                agent = next((a for a in network.agents if a.agent_id == agent_id), None)
                if agent:
                    node_colors.append(agent.judgment_tendency)
                else:
                    node_colors.append(0.0)
            else:
                node_colors.append(0.0)
    else:
        node_colors = 'lightblue'
    
    # Node sizes
    node_sizes = []
    if node_size_attribute == 'degree':
        degrees = dict(network.graph.degree())
        node_sizes = [300 + 100 * degrees.get(node_id, 0) for node_id in network.graph.nodes()]
    elif node_size_attribute == 'error_rate':
        for node_id in network.graph.nodes():
            agent_id = network.graph.nodes[node_id].get('agent_id')
            if agent_id is not None:
                agent = next((a for a in network.agents if a.agent_id == agent_id), None)
                if agent:
                    node_sizes.append(300 + 500 * agent.error_rate)
                else:
                    node_sizes.append(300)
            else:
                node_sizes.append(300)
    else:
        node_sizes = 500
    
    # Draw network
    nx.draw_networkx_nodes(network.graph, pos, node_color=node_colors, node_size=node_sizes,
                          alpha=0.8, cmap=plt.cm.RdYlGn_r, ax=ax)
    nx.draw_networkx_edges(network.graph, pos, alpha=0.3, width=1.5, ax=ax)
    
    # Labels (only for small networks)
    if len(network.graph.nodes()) <= 50:
        labels = {node_id: f"A{network.graph.nodes[node_id].get('agent_id', node_id)}" 
                 for node_id in network.graph.nodes()}
        nx.draw_networkx_labels(network.graph, pos, labels, font_size=8, ax=ax)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    
    # Add colorbar if using attribute coloring
    if isinstance(node_colors, list):
        sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn_r, 
                                  norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label(node_color_attribute.replace('_', ' ').title(), fontsize=11)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    
    return fig


def plot_opinion_propagation_animated(
    network: SocialNetwork,
    opinion_history: List[np.ndarray],
    time_steps: int,
    save_path: Optional[str] = None,
    interval: int = 300
) -> animation.FuncAnimation:
    """
    Create animated visualization of opinion propagation through network.
    
    Parameters
    ----------
    network : SocialNetwork
        Social network
    opinion_history : List[np.ndarray]
        History of opinions at each time step
    time_steps : int
        Number of time steps
    save_path : Optional[str], default=None
        Path to save animation
    interval : int, default=300
        Animation interval in milliseconds
        
    Returns
    -------
    animation.FuncAnimation
        Animation object
    """
    if len(network.graph.nodes()) == 0:
        print("Network is empty, cannot animate")
        return None
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Layout
    pos = nx.spring_layout(network.graph, k=1, iterations=50, seed=42)
    
    # Initialize
    nodes = nx.draw_networkx_nodes(network.graph, pos, node_color='lightblue', 
                                  node_size=500, alpha=0.8, ax=ax)
    edges = nx.draw_networkx_edges(network.graph, pos, alpha=0.3, width=1.5, ax=ax)
    
    ax.set_title('Opinion Propagation', fontsize=14, fontweight='bold')
    ax.axis('off')
    
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12,
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    def animate(frame):
        if frame < len(opinion_history):
            opinions = opinion_history[frame]
            
            # Update node colors based on opinions
            node_colors = opinions.tolist() if len(opinions) == len(network.graph.nodes()) else 'lightblue'
            
            ax.clear()
            ax.axis('off')
            nx.draw_networkx_nodes(network.graph, pos, node_color=node_colors, 
                                  node_size=500, alpha=0.8, cmap=plt.cm.coolwarm, 
                                  vmin=-1, vmax=1, ax=ax)
            nx.draw_networkx_edges(network.graph, pos, alpha=0.3, width=1.5, ax=ax)
            
            time_text = ax.text(0.02, 0.95, f'Time: t = {frame}', transform=ax.transAxes, 
                               fontsize=12, verticalalignment='top',
                               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            ax.set_title('Opinion Propagation', fontsize=14, fontweight='bold')
        
        return []
    
    anim = animation.FuncAnimation(
        fig, animate, frames=time_steps, interval=interval, blit=False, repeat=True
    )
    
    if save_path:
        try:
            anim.save(save_path, writer='ffmpeg', fps=3)
        except Exception as e:
            print(f"Could not save animation: {e}")
    
    return anim


def plot_error_density_on_network(
    network: SocialNetwork,
    error_density: Dict[int, float],
    save_path: Optional[str] = None,
    show: bool = True,
    title: str = "Error Density Distribution on Network"
) -> plt.Figure:
    """
    Visualize error density distribution on network.
    
    Parameters
    ----------
    network : SocialNetwork
        Social network
    error_density : Dict[int, float]
        Mapping from agent_id to error density
    save_path : Optional[str], default=None
        Path to save figure
    show : bool, default=True
        Whether to display
    title : str, default="Error Density Distribution on Network"
        Plot title
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    if len(network.graph.nodes()) == 0:
        print("Network is empty, cannot visualize")
        return None
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Layout
    pos = nx.spring_layout(network.graph, k=1, iterations=50, seed=42)
    
    # Node colors and sizes based on error density
    node_colors = []
    node_sizes = []
    
    for node_id in network.graph.nodes():
        agent_id = network.graph.nodes[node_id].get('agent_id')
        if agent_id is not None:
            density = error_density.get(agent_id, 0.0)
            node_colors.append(density)
            node_sizes.append(300 + 500 * density)
        else:
            node_colors.append(0.0)
            node_sizes.append(300)
    
    # Draw network
    nodes = nx.draw_networkx_nodes(network.graph, pos, node_color=node_colors, 
                                  node_size=node_sizes, alpha=0.8, cmap=plt.cm.Reds, ax=ax)
    nx.draw_networkx_edges(network.graph, pos, alpha=0.3, width=1.5, ax=ax)
    
    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, 
                              norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors)))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Error Density', fontsize=11)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    
    return fig


def plot_network_communities(
    network: SocialNetwork,
    communities: Dict[int, int],
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Visualize network with community detection coloring.
    
    Parameters
    ----------
    network : SocialNetwork
        Social network
    communities : Dict[int, int]
        Mapping from agent_id to community_id
    save_path : Optional[str], default=None
        Path to save figure
    show : bool, default=True
        Whether to display
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    if len(network.graph.nodes()) == 0:
        print("Network is empty, cannot visualize")
        return None
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Layout
    pos = nx.spring_layout(network.graph, k=1, iterations=50, seed=42)
    
    # Color nodes by community
    node_colors = []
    for node_id in network.graph.nodes():
        agent_id = network.graph.nodes[node_id].get('agent_id')
        if agent_id is not None:
            comm_id = communities.get(agent_id, 0)
            node_colors.append(comm_id)
        else:
            node_colors.append(0)
    
    # Use distinct colors for communities
    unique_communities = len(set(node_colors))
    cmap = plt.cm.get_cmap('tab20', unique_communities)
    
    nx.draw_networkx_nodes(network.graph, pos, node_color=node_colors, 
                          node_size=500, alpha=0.8, cmap=cmap, ax=ax)
    nx.draw_networkx_edges(network.graph, pos, alpha=0.3, width=1.5, ax=ax)
    
    ax.set_title(f'Network Communities (Found {unique_communities} communities)', 
                fontsize=14, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    
    return fig


def plot_centrality_comparison(
    network: SocialNetwork,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot comparison of different centrality measures.
    
    Parameters
    ----------
    network : SocialNetwork
        Social network
    save_path : Optional[str], default=None
        Path to save figure
    show : bool, default=True
        Whether to display
        
    Returns
    -------
    plt.Figure
        Figure object
    """
    centrality = network.get_centrality_measures()
    
    if len(centrality) == 0:
        print("No centrality data available")
        return None
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    # Extract data
    agent_ids = list(centrality.keys())
    degree_cent = [centrality[a]['degree_centrality'] for a in agent_ids]
    betweenness_cent = [centrality[a]['betweenness_centrality'] for a in agent_ids]
    closeness_cent = [centrality[a]['closeness_centrality'] for a in agent_ids]
    eigenvector_cent = [centrality[a]['eigenvector_centrality'] for a in agent_ids]
    
    # Plot 1: Degree centrality
    axes[0].bar(range(len(agent_ids)), degree_cent, color='steelblue', alpha=0.7, edgecolor='black')
    axes[0].set_xlabel('Agent ID', fontsize=11)
    axes[0].set_ylabel('Degree Centrality', fontsize=11)
    axes[0].set_title('Degree Centrality', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Betweenness centrality
    axes[1].bar(range(len(agent_ids)), betweenness_cent, color='coral', alpha=0.7, edgecolor='black')
    axes[1].set_xlabel('Agent ID', fontsize=11)
    axes[1].set_ylabel('Betweenness Centrality', fontsize=11)
    axes[1].set_title('Betweenness Centrality', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Closeness centrality
    axes[2].bar(range(len(agent_ids)), closeness_cent, color='lightgreen', alpha=0.7, edgecolor='black')
    axes[2].set_xlabel('Agent ID', fontsize=11)
    axes[2].set_ylabel('Closeness Centrality', fontsize=11)
    axes[2].set_title('Closeness Centrality', fontsize=12, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    
    # Plot 4: Eigenvector centrality
    axes[3].bar(range(len(agent_ids)), eigenvector_cent, color='gold', alpha=0.7, edgecolor='black')
    axes[3].set_xlabel('Agent ID', fontsize=11)
    axes[3].set_ylabel('Eigenvector Centrality', fontsize=11)
    axes[3].set_title('Eigenvector Centrality', fontsize=12, fontweight='bold')
    axes[3].grid(True, alpha=0.3)
    
    plt.suptitle('Network Centrality Measures Comparison', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    
    return fig


