"""
Hybrid Model Module

This module integrates all psychohistory components into a unified framework:
- Temporal ERH
- ABM simulation
- Network dynamics
- Fluid model
- Meta-monitoring

Provides a unified API for running complete psychohistory-style simulations.
"""

import numpy as np
from typing import List, Dict, Optional, Callable, Tuple
from .temporal_erh import track_error_evolution, compute_Pi_temporal, compute_E_temporal
from .abm_simulator import ABMSimulator
from .meta_monitor import MetaMonitor, ERHParameters
from .social_network import SocialNetwork
from .agent import AgentPopulation
from .action_space import Action, generate_world
from .judgement_system import BaseJudge

# Handle relative imports for both package and test environments
try:
    from ..analysis.opinion_dynamics import degroot_model, hegselmann_krause_model, aggregate_beliefs
    from ..analysis.fluid_model import solve_error_density_pde, fit_fluid_parameters, detect_critical_phenomena
    from ..analysis.temporal_analysis import analyze_temporal_trends, detect_anomalies, forecast_error_growth
except ImportError:
    # Fallback for test environments or direct execution
    from analysis.opinion_dynamics import degroot_model, hegselmann_krause_model, aggregate_beliefs
    from analysis.fluid_model import solve_error_density_pde, fit_fluid_parameters, detect_critical_phenomena
    from analysis.temporal_analysis import analyze_temporal_trends, detect_anomalies, forecast_error_growth


class HybridPsychohistoryModel:
    """
    Integrated psychohistory model combining all components.
    
    This class provides a unified interface for running complete
    psychohistory-style simulations with all features integrated.
    
    Attributes
    ----------
    abm_simulator : ABMSimulator
        ABM simulator component
    meta_monitor : MetaMonitor
        Meta-layer monitor
    temporal_enabled : bool
        Whether temporal tracking is enabled
    network_dynamics_enabled : bool
        Whether network dynamics are enabled
    fluid_model_enabled : bool
        Whether fluid model is enabled
    """
    
    def __init__(
        self,
        num_agents: int = 100,
        judge_factory: Optional[Callable[[int], BaseJudge]] = None,
        network_topology: str = 'small_world',
        enable_temporal: bool = True,
        enable_network_dynamics: bool = True,
        enable_fluid_model: bool = False,
        enable_meta_monitor: bool = True
    ):
        """
        Initialize hybrid model.
        
        Parameters
        ----------
        num_agents : int, default=100
            Number of agents
        judge_factory : Optional[Callable[[int], BaseJudge]], default=None
            Function to create judges
        network_topology : str, default='small_world'
            Network topology
        enable_temporal : bool, default=True
            Enable temporal ERH tracking
        enable_network_dynamics : bool, default=True
            Enable network opinion dynamics
        enable_fluid_model : bool, default=False
            Enable fluid model (computationally expensive)
        enable_meta_monitor : bool, default=True
            Enable meta-layer monitoring
        """
        # Initialize ABM simulator
        self.abm_simulator = ABMSimulator(
            num_agents=num_agents,
            judge_factory=judge_factory,
            network_topology=network_topology,
            enable_meta_monitor=enable_meta_monitor
        )
        
        self.meta_monitor = self.abm_simulator.meta_monitor
        
        # Feature flags
        self.temporal_enabled = enable_temporal
        self.network_dynamics_enabled = enable_network_dynamics
        self.fluid_model_enabled = enable_fluid_model
        
        # State
        self.simulation_state = {
            'time': 0,
            'erh_history': [],
            'network_history': [],
            'fluid_history': []
        }
    
    def run_simulation(
        self,
        num_time_steps: int = 10,
        actions_per_step: int = 1000,
        tau: float = 0.3,
        X_max: int = 100,
        network_dynamics_model: str = 'degroot',
        fluid_model_params: Optional[Dict] = None
    ) -> Dict:
        """
        Run complete hybrid simulation.
        
        Parameters
        ----------
        num_time_steps : int, default=10
            Number of time steps
        actions_per_step : int, default=1000
            Actions per time step
        tau : float, default=0.3
            Error threshold
        X_max : int, default=100
            Maximum complexity
        network_dynamics_model : str, default='degroot'
            Network dynamics model: 'degroot' or 'hegselmann_krause'
        fluid_model_params : Optional[Dict], default=None
            Parameters for fluid model
            
        Returns
        -------
        Dict
            Complete simulation results
        """
        # Run ABM simulation
        abm_results = self.abm_simulator.run_simulation(
            num_time_steps=num_time_steps,
            actions_per_step=actions_per_step,
            tau=tau,
            X_max=X_max,
            track_erh=self.temporal_enabled
        )
        
        results = {
            'abm_results': abm_results,
            'temporal_erh': None,
            'network_dynamics': None,
            'fluid_model': None,
            'meta_monitoring': None
        }
        
        # Temporal ERH analysis
        if self.temporal_enabled and 'actions_history' in abm_results:
            temporal_results = self.abm_simulator.compute_temporal_erh(
                abm_results['actions_history'],
                tau=tau,
                X_max=X_max
            )
            results['temporal_erh'] = temporal_results
            
            # Temporal analysis
            if 'E_xt' in temporal_results:
                E_xt = temporal_results['E_xt']
                time_steps = E_xt.shape[0]
                x_values = np.arange(1, X_max + 1)
                
                # Analyze trends
                trends = analyze_temporal_trends(E_xt, time_steps, x_values)
                results['temporal_trends'] = trends
                
                # Detect anomalies
                anomalies = detect_anomalies(E_xt, method='combined', X_max=X_max)
                results['anomalies'] = anomalies
                
                # Forecast
                forecast = forecast_error_growth(E_xt, forecast_horizon=5, X_max=X_max)
                results['forecast'] = forecast
        
        # Network dynamics
        if self.network_dynamics_enabled:
            network = self.abm_simulator.network
            agents = self.abm_simulator.population.agents
            
            if network_dynamics_model == 'degroot':
                dynamics_result = degroot_model(agents, network)
            elif network_dynamics_model == 'hegselmann_krause':
                dynamics_result = hegselmann_krause_model(agents, network)
            else:
                dynamics_result = {'converged': False, 'final_opinions': []}
            
            results['network_dynamics'] = dynamics_result
            
            # Aggregate beliefs
            individual_errors = {agent.agent_id: agent.error_rate for agent in agents}
            aggregated = aggregate_beliefs(individual_errors, network, dynamics_model=network_dynamics_model)
            results['aggregated_beliefs'] = aggregated
        
        # Fluid model (if enabled)
        if self.fluid_model_enabled and self.temporal_enabled and 'E_xt' in results.get('temporal_erh', {}):
            E_xt = results['temporal_erh']['E_xt']
            time_steps = E_xt.shape[0]
            
            # Fit fluid parameters from data
            x_values = np.arange(1, X_max + 1)
            t_values = np.arange(time_steps)
            fluid_params = fit_fluid_parameters(E_xt, x_values, t_values)
            
            # Solve fluid model
            if fluid_model_params is None:
                fluid_model_params = fluid_params
            
            try:
                u_xt, x_grid, t_grid = solve_error_density_pde(
                    x_range=(1, X_max),
                    t_range=(0, time_steps),
                    nx=min(50, X_max),
                    nt=min(50, time_steps),
                    v=fluid_model_params.get('v', 0.1),
                    D=fluid_model_params.get('D', 0.01),
                    alpha=fluid_model_params.get('alpha', 0.05)
                )
                
                # Detect critical phenomena
                critical_events = detect_critical_phenomena(u_xt, x_grid, t_grid)
                
                results['fluid_model'] = {
                    'u_xt': u_xt,
                    'x_grid': x_grid,
                    't_grid': t_grid,
                    'parameters': fluid_params,
                    'critical_events': critical_events
                }
            except Exception as e:
                results['fluid_model'] = {'error': str(e)}
        
        # Meta-monitoring summary
        if self.meta_monitor:
            results['meta_monitoring'] = self.meta_monitor.get_monitoring_summary()
        
        # Update state
        self.simulation_state['time'] = num_time_steps
        self.simulation_state['erh_history'] = abm_results.get('erh_history', [])
        
        return results
    
    def adaptive_adjustment(
        self,
        simulation_results: Dict,
        target_exponent: float = 0.5
    ) -> Dict:
        """
        Perform adaptive adjustment based on simulation results.
        
        Parameters
        ----------
        simulation_results : Dict
            Results from run_simulation
        target_exponent : float, default=0.5
            Target ERH exponent
            
        Returns
        -------
        Dict
            Adjustment results and recommendations
        """
        adjustments = {}
        
        # Meta-monitor adaptive parameters
        if self.meta_monitor and 'temporal_erh' in simulation_results:
            temporal_erh = simulation_results['temporal_erh']
            if 'E_xt' in temporal_erh:
                E_xt = temporal_erh['E_xt']
                # Use meta-monitor's adaptive adjustment
                E_xt_history = [E_xt]
                new_params = self.meta_monitor.adaptive_erh_parameters(E_xt_history, target_exponent)
                adjustments['erh_parameters'] = {
                    'C': new_params.C,
                    'epsilon': new_params.epsilon
                }
        
        # ABM calibration
        if 'abm_results' in simulation_results:
            calibration = self.abm_simulator.calibrate_erh_parameters(
                simulation_results['abm_results'],
                target_exponent
            )
            adjustments['abm_calibration'] = calibration
        
        return adjustments
    
    def get_unified_metrics(self, simulation_results: Dict) -> Dict:
        """
        Compute unified metrics across all components.
        
        Parameters
        ----------
        simulation_results : Dict
            Simulation results
            
        Returns
        -------
        Dict
            Unified metrics
        """
        metrics = {
            'erh_satisfaction': None,
            'temporal_stability': None,
            'network_coherence': None,
            'system_health': None
        }
        
        # ERH satisfaction
        if 'temporal_erh' in simulation_results:
            temporal_erh = simulation_results['temporal_erh']
            if 'erh_satisfaction' in temporal_erh:
                erh_sat = temporal_erh['erh_satisfaction']
                metrics['erh_satisfaction'] = {
                    'satisfaction_rate': erh_sat.get('satisfaction_rate', 0.0),
                    'violation_rate': erh_sat.get('violation_rate', 0.0),
                    'worst_violation': erh_sat.get('worst_violation', 0.0)
                }
        
        # Temporal stability
        if 'temporal_trends' in simulation_results:
            trends = simulation_results['temporal_trends']
            overall = trends.get('overall_trend', {})
            metrics['temporal_stability'] = {
                'volatility': overall.get('volatility', 0.0),
                'trend_direction': overall.get('direction', 'unknown'),
                'mean_error': overall.get('mean_error', 0.0)
            }
        
        # Network coherence
        if 'network_dynamics' in simulation_results:
            network_dyn = simulation_results['network_dynamics']
            metrics['network_coherence'] = {
                'converged': network_dyn.get('converged', False),
                'iterations': network_dyn.get('iterations', 0),
                'clusters': len(network_dyn.get('clusters', []))
            }
        
        # System health (composite metric)
        health_score = 1.0
        
        if metrics['erh_satisfaction']:
            satisfaction_rate = metrics['erh_satisfaction']['satisfaction_rate']
            health_score *= satisfaction_rate
        
        if metrics['temporal_stability']:
            volatility = metrics['temporal_stability']['volatility']
            # Lower volatility is better
            health_score *= max(0.0, 1.0 - volatility / 0.5)
        
        if metrics['network_coherence']:
            if metrics['network_coherence']['converged']:
                health_score *= 1.1  # Bonus for convergence
            else:
                health_score *= 0.9
        
        metrics['system_health'] = {
            'score': min(1.0, max(0.0, health_score)),
            'status': 'healthy' if health_score > 0.7 else 'degraded' if health_score > 0.4 else 'critical'
        }
        
        return metrics
    
    def get_summary(self) -> Dict:
        """
        Get summary of hybrid model state.
        
        Returns
        -------
        Dict
            Model summary
        """
        return {
            'num_agents': len(self.abm_simulator.population),
            'network_topology': self.abm_simulator.network.get_network_statistics(),
            'features_enabled': {
                'temporal': self.temporal_enabled,
                'network_dynamics': self.network_dynamics_enabled,
                'fluid_model': self.fluid_model_enabled,
                'meta_monitor': self.meta_monitor is not None
            },
            'simulation_state': self.simulation_state,
            'abm_summary': self.abm_simulator.get_simulation_summary()
        }

