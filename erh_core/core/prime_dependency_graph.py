"""
Prime Dependency Graph Module

This module implements a graph-based approach to identifying ethical primes
by analyzing error dependencies and structural fundamentality.

An ethical prime is defined as an error that, when corrected, significantly
reduces the global error rate. This is formalized using a dependency graph
where edges represent error relationships.
"""

import numpy as np
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict
import networkx as nx
from .action_space import Action


def build_error_dependency_graph(
    actions: List[Action],
    similarity_threshold: float = 0.3
) -> nx.Graph:
    """
    Build a graph representing dependencies between errors.
    
    Two errors are connected if:
    1. They occur in similar complexity ranges
    2. They have similar importance weights
    3. They represent similar types of misjudgments
    
    Parameters
    ----------
    actions : List[Action]
        List of actions that have been judged
    similarity_threshold : float, default=0.3
        Threshold for considering errors similar
        
    Returns
    -------
    nx.Graph
        Graph where nodes are mistakes and edges represent dependencies
    """
    mistakes = [a for a in actions if a.mistake_flag == 1]
    
    if len(mistakes) == 0:
        return nx.Graph()
    
    G = nx.Graph()
    
    # Add all mistakes as nodes
    for i, mistake in enumerate(mistakes):
        G.add_node(i, action=mistake)
    
    # Add edges between similar mistakes
    for i in range(len(mistakes)):
        for j in range(i + 1, len(mistakes)):
            a1, a2 = mistakes[i], mistakes[j]
            
            # Compute similarity metrics
            complexity_sim = 1.0 - abs(a1.c - a2.c) / max(a1.c, a2.c, 1)
            importance_sim = 1.0 - abs(a1.w - a2.w) / max(a1.w, a2.w, 0.001)
            error_sim = 1.0 - abs(abs(a1.delta) - abs(a2.delta)) / 2.0 if (a1.delta is not None and a2.delta is not None) else 0.0
            
            # Combined similarity
            total_sim = (complexity_sim + importance_sim + error_sim) / 3.0
            
            if total_sim > similarity_threshold:
                G.add_edge(i, j, weight=total_sim)
    
    return G


def compute_error_correction_impact(
    actions: List[Action],
    mistake_indices: List[int],
    tau: float = 0.3
) -> Dict[int, float]:
    """
    Compute the impact of correcting each mistake on global error rate.
    
    Impact is defined as:
    impact = (error_rate_before - error_rate_after) / error_rate_before
    
    Parameters
    ----------
    actions : List[Action]
        List of all actions
    mistake_indices : List[int]
        Indices of mistakes to evaluate
    tau : float, default=0.3
        Error threshold used in original evaluation
        
    Returns
    -------
    dict
        Mapping from mistake index to impact value
    """
    # Compute baseline error rate
    total_errors = sum(1 for a in actions if a.mistake_flag)
    total_actions = len(actions)
    baseline_error_rate = total_errors / total_actions if total_actions > 0 else 0.0
    
    impacts = {}
    
    for mistake_idx in mistake_indices:
        if mistake_idx >= len(actions):
            continue
        
        action = actions[mistake_idx]
        if not action.mistake_flag:
            impacts[mistake_idx] = 0.0
            continue
        
        # Simulate correcting this mistake
        # We estimate impact by considering how many similar errors might also be reduced
        # This is a heuristic - in practice, we'd need to know the correction mechanism
        
        # Count similar mistakes that might be affected
        similar_mistakes = 0
        for other_action in actions:
            if other_action.mistake_flag and other_action != action:
                # Similarity based on complexity and importance
                complexity_diff = abs(action.c - other_action.c) / max(action.c, other_action.c, 1)
                importance_diff = abs(action.w - other_action.w) / max(action.w, other_action.w, 0.001)
                
                if complexity_diff < 0.2 and importance_diff < 0.2:
                    similar_mistakes += 1
        
        # Estimate impact: correcting this mistake might reduce similar ones
        # Impact is proportional to importance, error magnitude, and number of similar mistakes
        error_magnitude = abs(action.delta) if action.delta is not None else 0.0
        estimated_reduction = action.w * error_magnitude * (1 + 0.1 * similar_mistakes)
        impact = estimated_reduction / max(baseline_error_rate, 0.001)
        
        # Normalize to reasonable range
        impact = min(impact, 1.0)
        impacts[mistake_idx] = impact
    
    return impacts


def select_primes_by_dependency(
    actions: List[Action],
    impact_threshold: float = 0.1,
    tau: float = 0.3,
    use_centrality: bool = True
) -> List[Action]:
    """
    Select ethical primes using dependency graph analysis.
    
    This method identifies fundamental errors by:
    1. Building error dependency graph
    2. Computing correction impact for each error
    3. Using graph centrality measures
    4. Selecting errors with high impact and centrality
    
    Parameters
    ----------
    actions : List[Action]
        List of actions that have been judged
    impact_threshold : float, default=0.1
        Minimum impact required to be considered a prime
    tau : float, default=0.3
        Error threshold
    use_centrality : bool, default=True
        Whether to use graph centrality in selection
        
    Returns
    -------
    List[Action]
        List of ethical primes selected by dependency analysis
    """
    mistakes = [a for a in actions if a.mistake_flag == 1]
    
    if len(mistakes) == 0:
        return []
    
    # Build dependency graph
    G = build_error_dependency_graph(actions)
    
    # Get mistake indices
    mistake_indices = [i for i, a in enumerate(actions) if a.mistake_flag]
    
    # Compute impact for each mistake
    impacts = compute_error_correction_impact(actions, mistake_indices, tau)
    
    # Compute centrality if requested
    centrality_scores = {}
    if use_centrality and G.number_of_nodes() > 0:
        try:
            # Use betweenness centrality as measure of structural importance
            betweenness = nx.betweenness_centrality(G)
            # Also consider degree centrality
            degree_cent = nx.degree_centrality(G)
            
            for node_idx in G.nodes():
                action_idx = mistake_indices[node_idx] if node_idx < len(mistake_indices) else None
                if action_idx is not None:
                    centrality_scores[action_idx] = (
                        betweenness.get(node_idx, 0.0) + 
                        degree_cent.get(node_idx, 0.0)
                    ) / 2.0
        except:
            # If centrality computation fails, use uniform scores
            for idx in mistake_indices:
                centrality_scores[idx] = 0.5
    
    # Score each mistake
    scored_mistakes = []
    for idx in mistake_indices:
        impact = impacts.get(idx, 0.0)
        centrality = centrality_scores.get(idx, 0.5) if use_centrality else 0.5
        
        # Combined score: weighted combination of impact and centrality
        score = 0.7 * impact + 0.3 * centrality
        
        if impact >= impact_threshold:
            scored_mistakes.append((idx, score, impact, centrality))
    
    # Sort by score and select top ones
    scored_mistakes.sort(key=lambda x: x[1], reverse=True)
    
    # Select top 10% or all that meet threshold
    num_to_select = max(1, int(len(mistakes) * 0.1))
    selected_indices = [idx for idx, _, _, _ in scored_mistakes[:num_to_select]]
    
    primes = [actions[idx] for idx in selected_indices]
    
    return primes


def analyze_error_decomposition(
    actions: List[Action],
    primes: List[Action]
) -> Dict:
    """
    Analyze which errors are "composite" (reducible) vs "atomic" (fundamental).
    
    Parameters
    ----------
    actions : List[Action]
        All actions
    primes : List[Action]
        Ethical primes identified
        
    Returns
    -------
    dict
        Analysis results including:
        - atomic_errors: Errors that cannot be decomposed
        - composite_errors: Errors that might be reducible
        - decomposition_ratio: Fraction of errors that are composite
    """
    all_mistakes = [a for a in actions if a.mistake_flag == 1]
    prime_set = set(primes)
    
    atomic_errors = []
    composite_errors = []
    
    for mistake in all_mistakes:
        if mistake in prime_set:
            atomic_errors.append(mistake)
        else:
            # Check if this mistake is "similar" to any prime
            # If so, it might be composite (reducible to that prime)
            is_composite = False
            for prime in primes:
                complexity_diff = abs(mistake.c - prime.c) / max(mistake.c, prime.c, 1)
                importance_diff = abs(mistake.w - prime.w) / max(mistake.w, prime.w, 0.001)
                
                if complexity_diff < 0.3 and importance_diff < 0.3:
                    is_composite = True
                    break
            
            if is_composite:
                composite_errors.append(mistake)
            else:
                # Not clearly composite, treat as potentially atomic
                atomic_errors.append(mistake)
    
    total_mistakes = len(all_mistakes)
    decomposition_ratio = len(composite_errors) / total_mistakes if total_mistakes > 0 else 0.0
    
    return {
        'atomic_errors': atomic_errors,
        'composite_errors': composite_errors,
        'decomposition_ratio': decomposition_ratio,
        'total_mistakes': total_mistakes,
        'primes': len(primes),
        'atomic_count': len(atomic_errors),
        'composite_count': len(composite_errors)
    }

