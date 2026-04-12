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

import hashlib
import os

import numpy as np
from typing import List, Dict, Optional, Callable, Tuple, Any
from .temporal_erh import track_error_evolution, compute_Pi_temporal, compute_E_temporal
from .abm_simulator import ABMSimulator
from .meta_monitor import MetaMonitor, ERHParameters
from .social_network import SocialNetwork
from .agent import AgentPopulation
from .action_space import Action, generate_world
from .judgement_system import BaseJudge

# Handle imports from analysis module
try:
    from erh_core.analysis.opinion_dynamics import degroot_model, hegselmann_krause_model, aggregate_beliefs
    from erh_core.analysis.fluid_model import solve_error_density_pde, fit_fluid_parameters, detect_critical_phenomena
    from erh_core.analysis.temporal_analysis import analyze_temporal_trends, detect_anomalies, forecast_error_growth
except ImportError:
    # Fallback for test environments or direct execution
    try:
        from ..analysis.opinion_dynamics import degroot_model, hegselmann_krause_model, aggregate_beliefs
        from ..analysis.fluid_model import solve_error_density_pde, fit_fluid_parameters, detect_critical_phenomena
        from ..analysis.temporal_analysis import analyze_temporal_trends, detect_anomalies, forecast_error_growth
    except ImportError:
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
        enable_meta_monitor: bool = True,
        enable_quantum: bool = False,
        quantum_agents_subsample: int = 4,
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
        enable_quantum : bool, default=False
            Enable quantum VQE stability estimation
        quantum_agents_subsample : int, default=4
            Max agents (qubits) for quantum simulation; subsample if population larger
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
        self.enable_quantum = enable_quantum
        self.quantum_agents_subsample = quantum_agents_subsample

        # Quantum state (lazy init)
        self._q_sim = None
        self._current_q_params = None
        self._hamiltonian_cache: Dict[str, Any] = {}

        # State
        self.simulation_state = {
            'time': 0,
            'erh_history': [],
            'network_history': [],
            'fluid_history': []
        }

    def _get_interaction_matrix(self, agents: List) -> np.ndarray:
        """Build similarity-based adjacency matrix from agents (error_rate)."""
        n = min(len(agents), self.quantum_agents_subsample)
        if n < 2:
            return np.zeros((1, 1))
        # Subsample uniformly if needed
        if len(agents) > n:
            step = max(1, len(agents) // n)
            idx = list(range(0, len(agents), step))[:n]
            agents = [agents[i] for i in idx]
        else:
            agents = list(agents)[:n]
        matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i < j:
                    w = 1.0 / (1.0 + abs(agents[i].error_rate - agents[j].error_rate))
                    matrix[i, j] = w
                    matrix[j, i] = w
        return matrix

    def _get_biases(self, agents: List) -> np.ndarray:
        """Extract biases from agents (judgment_tendency)."""
        n = min(len(agents), self.quantum_agents_subsample)
        if n < 1:
            return np.array([0.0])
        if len(agents) > n:
            step = max(1, len(agents) // n)
            idx = list(range(0, len(agents), step))[:n]
            agents = [agents[i] for i in idx]
        else:
            agents = list(agents)[:n]
        biases = np.array([np.clip(a.judgment_tendency, -1.0, 1.0) for a in agents])
        return biases

    def _get_cache_key(self, adj_matrix: np.ndarray, agent_data: list) -> str:
        """Generate unique hash for social state (adjacency + agent attributes)."""
        adj_bytes = np.asarray(adj_matrix).tobytes()
        arr = np.array(
            [
                [
                    a.get("empathy", 0.5),
                    a.get("flexibility", 0.5),
                    a.get("resilience", 0.5),
                ]
                for a in agent_data
            ],
            dtype=np.float64,
        )
        return hashlib.md5(adj_bytes + arr.tobytes()).hexdigest()

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
            'meta_monitoring': None,
            'quantum_stability': None,
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

        # Quantum Ethical Hilbert Space (AdvancedEthicalQuantumEngine)
        if self.enable_quantum:
            try:
                from simulation.quantum.simulator import AdvancedEthicalQuantumEngine

                agents = self.abm_simulator.population.agents
                if agents:
                    n_q = min(len(agents), self.quantum_agents_subsample, 20)
                    n_q = max(n_q, 2)
                    if self._q_sim is None:
                        use_ibm = os.environ.get("USE_IBM_QUANTUM", "").lower() in ("1", "true", "yes")
                        backend_name = os.environ.get("IBM_QUANTUM_BACKEND", "ibm_fez")
                        self._q_sim = AdvancedEthicalQuantumEngine(
                            num_agents=n_q,
                            use_real_hardware=use_ibm,
                            backend_name=backend_name,
                        )

                    active_agents = agents[:n_q] if len(agents) <= n_q else list(agents[i] for i in range(0, len(agents), max(1, len(agents) // n_q)))[:n_q]
                    agent_data = [
                        {
                            "empathy": getattr(a, "empathy", 1.0 - a.error_rate),
                            "flexibility": getattr(a, "flexibility", 0.5 + a.judgment_tendency / 2),
                            "resilience": getattr(a, "resilience", 1.0 - a.error_rate),
                        }
                        for a in active_agents
                    ]

                    network = self.abm_simulator.network
                    if hasattr(network, "get_adjacency_submatrix"):
                        adj_matrix = network.get_adjacency_submatrix(n_q)
                    else:
                        adj_matrix = self._get_interaction_matrix(active_agents)

                    cache_key = self._get_cache_key(adj_matrix, agent_data)
                    if cache_key in self._hamiltonian_cache:
                        q_results = self._hamiltonian_cache[cache_key]
                    else:
                        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        fig_dir = os.path.join(root, "simulation", "output", "figures")
                        q_results = self._q_sim.run_simulation(
                            agent_data, adj_matrix, output_dir=fig_dir
                        )
                        self._hamiltonian_cache[cache_key] = q_results

                    # Add quantum_energy (social_tension) via SocialDynamicsQuantumSimulator
                    biases = np.array([a.get("flexibility", 0.5) - 0.5 for a in agent_data], dtype=float)
                    try:
                        from simulation.quantum.simulator import SocialDynamicsQuantumSimulator

                        q_sim_ising = SocialDynamicsQuantumSimulator(
                            num_agents=adj_matrix.shape[0] if adj_matrix.size else 2,
                            topology="full",
                            seed=42,
                        )
                        quantum_energy = q_sim_ising.measure_social_tension(adj_matrix, biases)
                        q_results["quantum_energy"] = quantum_energy
                        q_results["social_tension_energy"] = quantum_energy
                        q_results["system_energy"] = quantum_energy
                    except Exception:
                        pass
                    q_results["magnetization"] = q_results.get("magnetization", q_results.get("system_coherence", 0.0))

                    if "raw_counts" in q_results:
                        try:
                            from erh_core.analysis.statistics import calculate_von_neumann_entropy

                            counts = q_results["raw_counts"]
                            if not counts:
                                raise ValueError("empty counts")
                            total = sum(counts.values())
                            n_qubits = len(next(iter(counts.keys())))
                            dim = 2 ** n_qubits
                            rho = np.zeros((dim, dim), dtype=np.float64)
                            for outcome, c in counts.items():
                                idx = int(outcome, 2) if outcome else 0
                                rho[idx, idx] = c / total if total else 0.0
                            q_results["von_neumann_entropy"] = calculate_von_neumann_entropy(rho)
                        except Exception:
                            pass
                    results["quantum_stability"] = q_results
            except ImportError:
                results["quantum_stability"] = {"error": "simulation.quantum not available"}
            except Exception as e:
                results["quantum_stability"] = {"error": str(e)}

        # Update state and simulation_history (C2.2)
        self.simulation_state['time'] = num_time_steps
        self.simulation_state['erh_history'] = abm_results.get('erh_history', [])
        if results.get('quantum_stability') and isinstance(results['quantum_stability'], dict):
            qs = results['quantum_stability']
            qe = qs.get('quantum_energy', qs.get('social_tension_energy'))
            vne = qs.get('von_neumann_entropy')
            self.simulation_state['quantum_energy'] = qe
            self.simulation_state['von_neumann_entropy'] = vne
            # Write to last simulation_history entry (C2.2)
            if self.abm_simulator.simulation_history:
                last = self.abm_simulator.simulation_history[-1]
                if isinstance(last, dict):
                    last['quantum_energy'] = qe
                    last['system_energy'] = qe
                    last['von_neumann_entropy'] = vne
                    last['magnetization'] = qs.get('magnetization', qs.get('system_coherence', 0.0))

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
                'meta_monitor': self.meta_monitor is not None,
                'quantum': self.enable_quantum,
            },
            'simulation_state': self.simulation_state,
            'abm_summary': self.abm_simulator.get_simulation_summary()
        }

