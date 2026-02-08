"""Core modules for action space, judgment systems, and ethical primes."""

# Re-export from shared core
try:
    from erh_core.core import *
except ImportError:
    # Fallback: try to import from local if erh_core not available
    # This maintains backward compatibility during transition
    from .action_space import Action, generate_world, calculate_complexity
    from .judgement_system import (
        BaseJudge,
        BiasedJudge,
        NoisyJudge,
        ConservativeJudge,
        RadicalJudge,
        GroundTruthProxy,
        evaluate_judgement,
    )
    from .ethical_primes import (
        select_ethical_primes,
        compute_Pi_and_error,
        analyze_error_growth,
    )
    
    # Psychohistory modules
    from .temporal_erh import (
        compute_Pi_temporal,
        compute_E_temporal,
        track_error_evolution,
        simulate_mule_effect,
        detect_mule_anomalies,
    )
    from .agent import EthicalAgent, AgentPopulation, SimpleEthicalAgent
    from .social_network import SocialNetwork
    from .meta_monitor import MetaMonitor, ERHParameters
    from .abm_simulator import ABMSimulator
    from .hybrid_model import HybridPsychohistoryModel
    
    __all__ = [
        "Action",
        "generate_world",
        "calculate_complexity",
        "BaseJudge",
        "BiasedJudge",
        "NoisyJudge",
        "ConservativeJudge",
        "RadicalJudge",
        "GroundTruthProxy",
        "evaluate_judgement",
        "select_ethical_primes",
        "compute_Pi_and_error",
        "analyze_error_growth",
        # Psychohistory
        "compute_Pi_temporal",
        "compute_E_temporal",
        "track_error_evolution",
        "simulate_mule_effect",
        "detect_mule_anomalies",
        "EthicalAgent",
        "AgentPopulation",
        "SimpleEthicalAgent",
        "SocialNetwork",
        "MetaMonitor",
        "ERHParameters",
        "ABMSimulator",
        "HybridPsychohistoryModel",
    ]
