"""
Core modules for Ethical Riemann Hypothesis.

This package contains the core simulation logic including:
- Action space generation
- Judgment systems
- Ethical primes computation
- Agent-based modeling
- Temporal ERH analysis
"""

# Import all core modules for easy access
from erh_core.core.action_space import Action, generate_world
from erh_core.core.judgement_system import (
    BaseJudge, BiasedJudge, NoisyJudge, ConservativeJudge, RadicalJudge,
    OracleDrivenJudge, CustomJudge,
    IntersectionalJudge, TemporalJudge, CounterfactualJudge, FederatedJudge,
    DecisionTrace,
    evaluate_judgement, batch_evaluate, compute_judgment_metrics,
)
from erh_core.analysis.erh_checks import (
    ERHCheckResult, check_erh_bound_structured, judge_and_check_erh,
)
from erh_core.core.ethical_primes import (
    select_ethical_primes, compute_Pi_and_error, analyze_error_growth
)
from erh_core.core.agent import EthicalAgent, AgentPopulation, SimpleEthicalAgent
from erh_core.core.social_network import SocialNetwork
from erh_core.core.meta_monitor import MetaMonitor, ERHParameters
from erh_core.core.abm_simulator import ABMSimulator
from erh_core.core.hybrid_model import HybridPsychohistoryModel
from erh_core.core.temporal_erh import (
    track_error_evolution, compute_Pi_temporal, compute_E_temporal
)

__all__ = [
    "Action", "generate_world",
    "BaseJudge", "BiasedJudge", "NoisyJudge", "ConservativeJudge", "RadicalJudge",
    "OracleDrivenJudge", "CustomJudge",
    "IntersectionalJudge", "TemporalJudge", "CounterfactualJudge", "FederatedJudge",
    "DecisionTrace",
    "evaluate_judgement", "batch_evaluate", "compute_judgment_metrics",
    "ERHCheckResult", "check_erh_bound_structured", "judge_and_check_erh",
    "select_ethical_primes", "compute_Pi_and_error", "analyze_error_growth",
    "EthicalAgent", "AgentPopulation", "SimpleEthicalAgent",
    "SocialNetwork",
    "MetaMonitor", "ERHParameters",
    "ABMSimulator",
    "HybridPsychohistoryModel",
    "track_error_evolution", "compute_Pi_temporal", "compute_E_temporal",
]

