"""
Core modules: thin re-export from erh_core (Single Source of Truth).
Adds scenario_generator (erh-only).
"""

from erh_core.core.action_space import Action, generate_world
from erh_core.core.judgement_system import (
    BaseJudge,
    BiasedJudge,
    NoisyJudge,
    ConservativeJudge,
    RadicalJudge,
    evaluate_judgement,
)
from erh_core.core.ethical_primes import (
    select_ethical_primes,
    compute_Pi_and_error,
    analyze_error_growth,
)
from erh_core.core.agent import EthicalAgent, AgentPopulation, SimpleEthicalAgent
from erh_core.core.social_network import SocialNetwork
from erh_core.core.meta_monitor import MetaMonitor, ERHParameters
from erh_core.core.abm_simulator import ABMSimulator
from erh_core.core.hybrid_model import HybridPsychohistoryModel
from erh_core.core.temporal_erh import (
    compute_Pi_temporal,
    compute_E_temporal,
    track_error_evolution,
    simulate_mule_effect,
    detect_mule_anomalies,
)

# erh-only: scenario_generator
from .scenario_generator import (
    action_to_scenario_text,
    actions_to_prompts,
    DEFAULT_SYSTEM_PROMPT,
)

# ethical_primality_test: erh_core may not have it, try fallback
try:
    from erh_core.core.ethical_primes import ethical_primality_test
except ImportError:
    try:
        from .ethical_primes import ethical_primality_test
    except ImportError:
        ethical_primality_test = None  # type: ignore[assignment]

__all__ = [
    "Action",
    "generate_world",
    "BaseJudge",
    "BiasedJudge",
    "NoisyJudge",
    "ConservativeJudge",
    "RadicalJudge",
    "evaluate_judgement",
    "select_ethical_primes",
    "compute_Pi_and_error",
    "analyze_error_growth",
    "ethical_primality_test",
    "action_to_scenario_text",
    "actions_to_prompts",
    "DEFAULT_SYSTEM_PROMPT",
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
