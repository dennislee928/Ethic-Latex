"""
ABM Simulator Module

This module implements a complete Agent-Based Modeling (ABM) simulator for
psychohistory-style simulations of ethical judgment systems.

The simulator manages:
- Large populations of AI judgment agents (thousands)
- Agent interaction mechanisms
- Built-in ERH computation modules
- Dynamic tracking of Π(x,t) and E(x,t)
- Evaluation of ERH satisfaction
- Simulation result calibration
"""

import numpy as np
from typing import List, Dict, Optional, Callable, Tuple
from .agent import EthicalAgent, AgentPopulation, SimpleEthicalAgent
from .social_network import SocialNetwork
from .action_space import Action, generate_world
from .judgement_system import BaseJudge, evaluate_judgement
from .ethical_primes import select_ethical_primes, compute_Pi_and_error, analyze_error_growth
from .temporal_erh import track_error_evolution, compute_Pi_temporal, compute_E_temporal
from .meta_monitor import MetaMonitor


class ABMSimulator:
    """
    Agent-Based Modeling simulator for ethical judgment systems.
    
    Manages large populations of agents, their interactions, and tracks
    ERH metrics dynamically throughout the simulation.
    
    Attributes
    ----------
    population : AgentPopulation
        Population of agents
    network : SocialNetwork
        Social network structure
    meta_monitor : Optional[MetaMonitor]
        Meta-layer monitor (optional)
    simulation_history : List[Dict]
        History of simulation states
    """
    
    def __init__(
        self,
        num_agents: int = 100,
        judge_factory: Optional[Callable[[int], BaseJudge]] = None,
        network_topology: str = 'small_world',
        enable_meta_monitor: bool = True
    ):
        """
        Initialize ABM simulator.
        
        Parameters
        ----------
        num_agents : int, default=100
            Number of agents in population
        judge_factory : Optional[Callable[[int], BaseJudge]], default=None
            Function to create judge for agent i. If None, uses default.
        network_topology : str, default='small_world'
            Network topology for agent interactions
        enable_meta_monitor : bool, default=True
            Whether to enable meta-layer monitoring
        """
        # Create population
        self.population = AgentPopulation()
        
        if judge_factory is None:
            def default_judge_factory(i):
                from .judgement_system import BiasedJudge
                bias = 0.1 + 0.1 * (i % 5) / 5  # Vary bias
                return BiasedJudge(bias_strength=bias, name=f"Judge_{i}")
            judge_factory = default_judge_factory
        
        self.population.create_population(num_agents, judge_factory, SimpleEthicalAgent)
        
        # Create network
        self.network = SocialNetwork(
            agents=self.population.agents,
            topology=network_topology,
            n_nodes=num_agents
        )
        
        # Meta-monitor
        self.meta_monitor = MetaMonitor() if enable_meta_monitor else None
        
        # Simulation state
        self.simulation_history = []
        self.current_time = 0
    
    def run_simulation(
        self,
        num_time_steps: int = 10,
        actions_per_step: int = 1000,
        tau: float = 0.3,
        X_max: int = 100,
        track_erh: bool = True,
        interaction_probability: float = 0.1
    ) -> Dict:
        """
        Run ABM simulation for multiple time steps.
        
        Parameters
        ----------
        num_time_steps : int, default=10
            Number of time steps
        actions_per_step : int, default=1000
            Number of actions to generate per time step
        tau : float, default=0.3
            Error threshold
        X_max : int, default=100
            Maximum complexity
        track_erh : bool, default=True
            Whether to track ERH metrics
        interaction_probability : float, default=0.1
            Probability of agent interactions per step
            
        Returns
        -------
        Dict
            Simulation results:
            - 'erh_history': History of ERH metrics
            - 'population_history': Population statistics over time
            - 'final_state': Final simulation state
        """
        erh_history = []
        population_history = []
        actions_history = []
        
        for t in range(num_time_steps):
            # Generate actions for this time step
            actions = generate_world(
                num_actions=actions_per_step,
                random_seed=42 + t
            )
            actions_history.append(actions)
            
            # Evaluate actions with all agents
            agent_results = self.population.evaluate_actions(actions, tau=tau)
            
            # Track ERH if enabled
            if track_erh:
                # Aggregate results across agents
                all_primes = []
                for agent_id, evaluated_actions in agent_results.items():
                    primes = select_ethical_primes(evaluated_actions)
                    all_primes.extend(primes)
                
                # Compute ERH metrics
                if len(all_primes) > 0:
                    Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(all_primes, X_max=X_max)
                    erh_analysis = analyze_error_growth(E_x, x_vals)
                    
                    erh_history.append({
                        'time': t,
                        'Pi_x': Pi_x,
                        'B_x': B_x,
                        'E_x': E_x,
                        'x_values': x_vals,
                        'analysis': erh_analysis,
                        'num_primes': len(all_primes)
                    })
                else:
                    erh_history.append({
                        'time': t,
                        'num_primes': 0,
                        'analysis': {'erh_satisfied': False}
                    })
            
            # Agent interactions (scheduled via population, weighted by network)
            self.population.schedule_interactions(
                interaction_rule=lambda a1, a2: self.network.get_influence_strength(a1, a2),
                interaction_probability=interaction_probability
            )
            
            # Update network attributes
            self.network.update_node_attributes()
            
            # Population statistics
            pop_stats = self.population.get_population_statistics()
            pop_stats['time'] = t
            population_history.append(pop_stats)
            
            # Meta-monitoring
            if self.meta_monitor and track_erh and len(erh_history) > 0:
                # Build E_xt array for monitoring
                if t == 0:
                    E_xt = np.zeros((1, X_max))
                    if len(erh_history) > 0 and 'E_x' in erh_history[-1]:
                        E_xt[0, :] = erh_history[-1]['E_x']
                else:
                    # Extend E_xt
                    new_E_x = erh_history[-1].get('E_x', np.zeros(X_max))
                    E_xt = np.vstack([E_xt, new_E_x.reshape(1, -1)])
                
                # Monitor
                monitor_result = self.meta_monitor.monitor(E_xt, t, X_max)
                if monitor_result.get('correction_applied'):
                    # Parameters were adjusted
                    pass
            
            self.current_time = t
        
        # Final state
        final_state = {
            'population_stats': self.population.get_population_statistics(),
            'network_stats': self.network.get_network_statistics(),
            'time': self.current_time
        }
        
        # Store in history
        self.simulation_history.append({
            'erh_history': erh_history,
            'population_history': population_history,
            'final_state': final_state
        })
        
        return {
            'erh_history': erh_history,
            'population_history': population_history,
            'final_state': final_state,
            'actions_history': actions_history
        }
    
    def compute_temporal_erh(
        self,
        actions_history: List[List[Action]],
        tau: float = 0.3,
        X_max: int = 100
    ) -> Dict:
        """
        Compute temporal ERH metrics from simulation history.
        
        Parameters
        ----------
        actions_history : List[List[Action]]
            History of actions at each time step
        tau : float, default=0.3
            Error threshold
        X_max : int, default=100
            Maximum complexity
            
        Returns
        -------
        Dict
            Temporal ERH results:
            - 'Pi_xt': Π(x,t) array
            - 'E_xt': E(x,t) array
            - 'erh_satisfaction': ERH satisfaction over time
        """
        # Aggregate primes across all agents at each time step
        primes_history = []
        
        for t, actions in enumerate(actions_history):
            # Evaluate with representative agent (first agent)
            if len(self.population.agents) > 0:
                actions_copy = [Action(id=a.id, c=a.c, V=a.V, w=a.w) for a in actions]
                agent = self.population.agents[0]
                for action in actions_copy:
                    agent.judge_action(action, tau=tau)
                primes = select_ethical_primes(actions_copy)
                primes_history.append(primes)
            else:
                primes_history.append([])
        
        # Compute temporal functions
        time_steps = len(primes_history)
        Pi_xt = compute_Pi_temporal(primes_history, time_steps, X_max)
        
        # Baseline (simplified - can be improved)
        from .temporal_erh import compute_baseline_temporal
        B_xt = compute_baseline_temporal(time_steps, X_max)
        
        # Error
        E_xt = compute_E_temporal(Pi_xt, B_xt, time_steps, X_max)
        
        # ERH satisfaction
        try:
            from ..analysis.temporal_analysis import compute_temporal_erh_satisfaction
        except ImportError:
            from analysis.temporal_analysis import compute_temporal_erh_satisfaction
        erh_satisfaction = compute_temporal_erh_satisfaction(E_xt, X_max=X_max)
        
        return {
            'Pi_xt': Pi_xt,
            'B_xt': B_xt,
            'E_xt': E_xt,
            'erh_satisfaction': erh_satisfaction,
            'primes_history': primes_history
        }
    
    def calibrate_erh_parameters(
        self,
        simulation_results: Dict,
        target_exponent: float = 0.5
    ) -> Dict:
        """
        Calibrate ERH parameters based on simulation results.
        
        Parameters
        ----------
        simulation_results : Dict
            Results from run_simulation
        target_exponent : float, default=0.5
            Target ERH exponent
            
        Returns
        -------
        Dict
            Calibrated parameters and recommendations
        """
        if 'erh_history' not in simulation_results:
            return {'calibrated': False, 'reason': 'No ERH history available'}
        
        erh_history = simulation_results['erh_history']
        
        # Collect all error data
        all_E_x = []
        for entry in erh_history:
            if 'E_x' in entry:
                all_E_x.append(entry['E_x'])
        
        if len(all_E_x) == 0:
            return {'calibrated': False, 'reason': 'No error data available'}
        
        # Aggregate analysis
        exponents = []
        erh_satisfied_count = 0
        
        for entry in erh_history:
            analysis = entry.get('analysis', {})
            exp = analysis.get('estimated_exponent', np.nan)
            if not np.isnan(exp):
                exponents.append(exp)
            if analysis.get('erh_satisfied', False):
                erh_satisfied_count += 1
        
        mean_exponent = np.mean(exponents) if exponents else np.nan
        satisfaction_rate = erh_satisfied_count / len(erh_history) if len(erh_history) > 0 else 0.0
        
        # Recommendations
        recommendations = []
        if mean_exponent > target_exponent + 0.1:
            recommendations.append("Reduce bias strength in judges")
            recommendations.append("Increase noise filtering")
        elif mean_exponent < target_exponent - 0.1:
            recommendations.append("System is performing better than ERH predicts")
        
        if satisfaction_rate < 0.5:
            recommendations.append("System frequently violates ERH - consider parameter adjustment")
        
        return {
            'calibrated': True,
            'mean_exponent': mean_exponent,
            'target_exponent': target_exponent,
            'satisfaction_rate': satisfaction_rate,
            'recommendations': recommendations
        }
    
    def get_simulation_summary(self) -> Dict:
        """
        Get summary of simulation state.
        
        Returns
        -------
        Dict
            Simulation summary
        """
        return {
            'current_time': self.current_time,
            'num_agents': len(self.population),
            'population_stats': self.population.get_population_statistics(),
            'network_stats': self.network.get_network_statistics(),
            'meta_monitor_active': self.meta_monitor is not None and self.meta_monitor.monitoring_active,
            'simulation_steps_completed': len(self.simulation_history)
        }

