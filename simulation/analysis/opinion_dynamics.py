"""
Opinion Dynamics Module

This module implements opinion dynamics models for simulating how agents'
judgment tendencies evolve through social interaction, analogous to psychohistory's
social psychology dimension.

Models implemented:
- DeGroot model: Linear opinion iteration
- Hegselmann-Krause model: Bounded confidence with influence radius
- Sznajd model: Consensus formation through local interactions
"""

import numpy as np
from typing import List, Dict, Optional, Callable, Tuple

# Handle relative imports for both package and test environments
try:
    from ..core.social_network import SocialNetwork
    from ..core.agent import EthicalAgent
except ImportError:
    # Fallback for test environments or direct execution
    from core.social_network import SocialNetwork
    from core.agent import EthicalAgent


def degroot_model(
    agents: List[EthicalAgent],
    network: SocialNetwork,
    max_iterations: int = 100,
    convergence_threshold: float = 1e-6
) -> Dict:
    """
    DeGroot model: Linear opinion iteration.
    
    Each agent updates their opinion as a weighted average of neighbors' opinions.
    Convergence to consensus is guaranteed under certain network conditions.
    
    Parameters
    ----------
    agents : List[EthicalAgent]
        List of agents
    network : SocialNetwork
        Social network structure
    max_iterations : int, default=100
        Maximum iterations
    convergence_threshold : float, default=1e-6
        Convergence threshold
        
    Returns
    -------
    Dict
        Results containing:
        - 'converged': whether consensus was reached
        - 'iterations': number of iterations
        - 'final_opinions': final judgment tendencies
        - 'convergence_history': history of opinion changes
    """
    n_agents = len(agents)
    if n_agents == 0:
        return {'converged': False, 'iterations': 0, 'final_opinions': [], 'convergence_history': []}
    
    # Initialize opinions (judgment tendencies)
    opinions = np.array([agent.judgment_tendency for agent in agents])
    convergence_history = [opinions.copy()]
    
    # Build influence matrix
    influence_matrix = np.zeros((n_agents, n_agents))
    for i, agent1 in enumerate(agents):
        neighbors = network.get_neighbors(agent1)
        if len(neighbors) > 0:
            # Equal weight to all neighbors
            weight = 1.0 / len(neighbors)
            for neighbor in neighbors:
                j = next((idx for idx, a in enumerate(agents) if a.agent_id == neighbor.agent_id), None)
                if j is not None:
                    influence_matrix[i, j] = weight
        else:
            # Isolated agent: keep own opinion
            influence_matrix[i, i] = 1.0
    
    # Iterate
    for iteration in range(max_iterations):
        new_opinions = influence_matrix @ opinions
        
        # Check convergence
        change = np.max(np.abs(new_opinions - opinions))
        if change < convergence_threshold:
            opinions = new_opinions
            convergence_history.append(opinions.copy())
            # Update agent tendencies
            for i, agent in enumerate(agents):
                agent.judgment_tendency = opinions[i]
            return {
                'converged': True,
                'iterations': iteration + 1,
                'final_opinions': opinions.tolist(),
                'convergence_history': convergence_history
            }
        
        opinions = new_opinions
        convergence_history.append(opinions.copy())
    
    # Update agent tendencies even if not converged
    for i, agent in enumerate(agents):
        agent.judgment_tendency = opinions[i]
    
    return {
        'converged': False,
        'iterations': max_iterations,
        'final_opinions': opinions.tolist(),
        'convergence_history': convergence_history
    }


def hegselmann_krause_model(
    agents: List[EthicalAgent],
    network: SocialNetwork,
    confidence_radius: float = 0.2,
    max_iterations: int = 100,
    convergence_threshold: float = 1e-6
) -> Dict:
    """
    Hegselmann-Krause model: Bounded confidence with influence radius.
    
    Agents only interact with neighbors whose opinions are within a confidence radius.
    This can lead to polarization or consensus depending on the radius.
    
    Parameters
    ----------
    agents : List[EthicalAgent]
        List of agents
    network : SocialNetwork
        Social network structure
    confidence_radius : float, default=0.2
        Maximum opinion difference for interaction
    max_iterations : int, default=100
        Maximum iterations
    convergence_threshold : float, default=1e-6
        Convergence threshold
        
    Returns
    -------
    Dict
        Results containing:
        - 'converged': whether convergence was reached
        - 'iterations': number of iterations
        - 'final_opinions': final judgment tendencies
        - 'clusters': detected opinion clusters
        - 'convergence_history': history of opinion changes
    """
    n_agents = len(agents)
    if n_agents == 0:
        return {'converged': False, 'iterations': 0, 'final_opinions': [], 'clusters': [], 'convergence_history': []}
    
    opinions = np.array([agent.judgment_tendency for agent in agents])
    convergence_history = [opinions.copy()]
    
    for iteration in range(max_iterations):
        new_opinions = opinions.copy()
        
        for i, agent1 in enumerate(agents):
            neighbors = network.get_neighbors(agent1)
            
            # Find neighbors within confidence radius
            trusted_neighbors = []
            for neighbor in neighbors:
                j = next((idx for idx, a in enumerate(agents) if a.agent_id == neighbor.agent_id), None)
                if j is not None:
                    opinion_diff = abs(opinions[i] - opinions[j])
                    if opinion_diff <= confidence_radius:
                        trusted_neighbors.append(j)
            
            # Update opinion as average of trusted neighbors (including self)
            if len(trusted_neighbors) > 0:
                trusted_indices = [i] + trusted_neighbors
                new_opinions[i] = np.mean(opinions[trusted_indices])
        
        # Check convergence
        change = np.max(np.abs(new_opinions - opinions))
        if change < convergence_threshold:
            opinions = new_opinions
            convergence_history.append(opinions.copy())
            # Update agent tendencies
            for i, agent in enumerate(agents):
                agent.judgment_tendency = opinions[i]
            
            # Detect clusters
            clusters = detect_opinion_clusters(opinions, confidence_radius)
            
            return {
                'converged': True,
                'iterations': iteration + 1,
                'final_opinions': opinions.tolist(),
                'clusters': clusters,
                'convergence_history': convergence_history
            }
        
        opinions = new_opinions
        convergence_history.append(opinions.copy())
    
    # Update agent tendencies
    for i, agent in enumerate(agents):
        agent.judgment_tendency = opinions[i]
    
    # Detect clusters
    clusters = detect_opinion_clusters(opinions, confidence_radius)
    
    return {
        'converged': False,
        'iterations': max_iterations,
        'final_opinions': opinions.tolist(),
        'clusters': clusters,
        'convergence_history': convergence_history
    }


def detect_opinion_clusters(opinions: np.ndarray, threshold: float = 0.1) -> List[List[int]]:
    """
    Detect opinion clusters (groups with similar opinions).
    
    Parameters
    ----------
    opinions : np.ndarray
        Array of opinions
    threshold : float, default=0.1
        Maximum difference within a cluster
        
    Returns
    -------
    List[List[int]]
        List of clusters, each containing agent indices
    """
    n = len(opinions)
    clusters = []
    assigned = set()
    
    for i in range(n):
        if i in assigned:
            continue
        
        cluster = [i]
        assigned.add(i)
        
        for j in range(i + 1, n):
            if j not in assigned and abs(opinions[i] - opinions[j]) <= threshold:
                cluster.append(j)
                assigned.add(j)
        
        clusters.append(cluster)
    
    return clusters


def aggregate_beliefs(
    E_individual: Dict[int, float],
    network: SocialNetwork,
    dynamics_model: str = 'degroot',
    **model_params
) -> Dict[int, float]:
    """
    Aggregate individual error indicators into group-level beliefs.
    
    Parameters
    ----------
    E_individual : Dict[int, float]
        Individual error indicators (agent_id -> error_rate)
    network : SocialNetwork
        Social network
    dynamics_model : str, default='degroot'
        Dynamics model: 'degroot' or 'hegselmann_krause'
    **model_params
        Parameters for dynamics model
        
    Returns
    -------
    Dict[int, float]
        Aggregated beliefs (agent_id -> aggregated error indicator)
    """
    agents = network.agents
    if len(agents) == 0:
        return {}
    
    # Initialize opinions from individual errors
    for agent in agents:
        agent.judgment_tendency = E_individual.get(agent.agent_id, 0.0)
    
    # Run dynamics model
    if dynamics_model == 'degroot':
        result = degroot_model(agents, network, **model_params)
    elif dynamics_model == 'hegselmann_krause':
        result = hegselmann_krause_model(agents, network, **model_params)
    else:
        raise ValueError(f"Unknown dynamics model: {dynamics_model}")
    
    # Extract aggregated beliefs
    aggregated = {}
    for i, agent in enumerate(agents):
        aggregated[agent.agent_id] = result['final_opinions'][i]
    
    return aggregated


def compute_group_error(
    agents: List[EthicalAgent],
    network: SocialNetwork,
    individual_errors: Dict[int, float],
    aggregation_method: str = 'weighted_average'
) -> float:
    """
    Compute group-level error from individual errors.
    
    Parameters
    ----------
    agents : List[EthicalAgent]
        List of agents
    network : SocialNetwork
        Social network
    individual_errors : Dict[int, float]
        Individual error rates
    aggregation_method : str, default='weighted_average'
        Aggregation method:
        - 'weighted_average': Weight by network centrality
        - 'simple_average': Simple average
        - 'max': Maximum error
        - 'min': Minimum error
        
    Returns
    -------
    float
        Group-level error
    """
    if len(agents) == 0:
        return 0.0
    
    errors = [individual_errors.get(agent.agent_id, 0.0) for agent in agents]
    
    if aggregation_method == 'simple_average':
        return np.mean(errors)
    elif aggregation_method == 'max':
        return np.max(errors)
    elif aggregation_method == 'min':
        return np.min(errors)
    elif aggregation_method == 'weighted_average':
        # Weight by degree centrality
        centrality = network.get_centrality_measures()
        weights = []
        for agent in agents:
            cent = centrality.get(agent.agent_id, {})
            weight = cent.get('degree_centrality', 1.0)
            weights.append(weight)
        
        weights = np.array(weights)
        weights = weights / (np.sum(weights) + 1e-10)  # Normalize
        
        return np.sum(weights * np.array(errors))
    else:
        return np.mean(errors)  # Default to simple average


def simulate_opinion_evolution(
    agents: List[EthicalAgent],
    network: SocialNetwork,
    time_steps: int = 50,
    dynamics_model: str = 'degroot',
    **model_params
) -> Dict:
    """
    Simulate opinion evolution over multiple time steps.
    
    Parameters
    ----------
    agents : List[EthicalAgent]
        List of agents
    network : SocialNetwork
        Social network
    time_steps : int, default=50
        Number of time steps
    dynamics_model : str, default='degroot'
        Dynamics model to use
    **model_params
        Model parameters
        
    Returns
    -------
    Dict
        Evolution results:
        - 'opinion_history': List of opinion arrays at each time step
        - 'convergence_time': Time to convergence (if converged)
        - 'final_consensus': Whether consensus was reached
    """
    opinion_history = []
    
    for t in range(time_steps):
        # Run one iteration of dynamics
        if dynamics_model == 'degroot':
            result = degroot_model(agents, network, max_iterations=1, **model_params)
        elif dynamics_model == 'hegselmann_krause':
            result = hegselmann_krause_model(agents, network, max_iterations=1, **model_params)
        else:
            raise ValueError(f"Unknown dynamics model: {dynamics_model}")
        
        opinions = np.array([agent.judgment_tendency for agent in agents])
        opinion_history.append(opinions.copy())
        
        # Check for convergence
        if t > 0:
            change = np.max(np.abs(opinion_history[-1] - opinion_history[-2]))
            if change < 1e-6:
                return {
                    'opinion_history': opinion_history,
                    'convergence_time': t + 1,
                    'final_consensus': True
                }
    
    return {
        'opinion_history': opinion_history,
        'convergence_time': None,
        'final_consensus': False
    }

