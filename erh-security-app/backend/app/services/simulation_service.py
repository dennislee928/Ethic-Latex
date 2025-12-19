"""
Service layer for interfacing with simulation modules.

This module provides a bridge between the FastAPI backend and the simulation
Python modules for running psychohistory simulations.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import json
from datetime import datetime

# Add project root to path to import simulation and erh_core
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

try:
    from erh_core.core.action_space import generate_world, Action
    from erh_core.core.judgement_system import (
        BiasedJudge,
        NoisyJudge,
        ConservativeJudge,
        evaluate_judgement,
    )
    from erh_core.core.ethical_primes import (
        select_ethical_primes,
        compute_Pi_and_error,
        analyze_error_growth,
    )
    from erh_core.analysis.statistics import bootstrap_exponent_ci
except ImportError as e:
    logger.warning(f"Could not import simulation modules: {e}. Simulations may not work.")
    generate_world = None
    evaluate_judgement = None
    select_ethical_primes = None
    compute_Pi_and_error = None
    analyze_error_growth = None


def run_simulation(
    num_actions: int = 1000,
    complexity_dist: str = "zipf",
    tau: float = 0.3,
    random_seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run a psychohistory simulation.

    Args:
        num_actions: Number of actions to generate
        complexity_dist: Distribution type ('zipf', 'uniform', 'power_law')
        tau: Threshold parameter for judgment evaluation
        random_seed: Random seed for reproducibility

    Returns:
        Dictionary containing simulation results:
        - mistake_rate: Proportion of misjudgments
        - ethical_primes_count: Number of ethical primes
        - analysis: Analysis results including ERH satisfaction
        - config: Configuration used
    """
    if generate_world is None:
        raise RuntimeError("Simulation modules not available. Cannot run simulation.")

    try:
        # Generate world
        logger.info(f"Generating world with {num_actions} actions, distribution={complexity_dist}")
        actions = generate_world(
            num_actions=num_actions,
            complexity_dist=complexity_dist,
            random_seed=random_seed,
        )

        # Create judge
        judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)

        # Evaluate actions
        logger.info(f"Evaluating {len(actions)} actions with tau={tau}")
        evaluate_judgement(actions, judge, tau=tau)

        # Count mistakes
        mistakes = sum(1 for a in actions if hasattr(a, 'mistake_flag') and a.mistake_flag)
        mistake_rate = mistakes / len(actions) if actions else 0.0

        # Extract ethical primes
        logger.info("Selecting ethical primes")
        primes = select_ethical_primes(actions, importance_quantile=0.9)

        # Compute error distribution
        logger.info("Computing error distribution")
        Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)

        # Analyze error growth
        logger.info("Analyzing error growth")
        growth_analysis = analyze_error_growth(E_x, x_vals)

        # Bootstrap confidence intervals
        try:
            ci_results = bootstrap_exponent_ci(E_x, x_vals, n_bootstrap=500)
            alpha_ci_low = ci_results.get("ci_lower", growth_analysis.get("estimated_exponent", 0.5))
            alpha_ci_high = ci_results.get("ci_upper", growth_analysis.get("estimated_exponent", 0.5))
        except Exception as e:
            logger.warning(f"Bootstrap CI failed: {e}")
            alpha_ci_low = growth_analysis.get("estimated_exponent", 0.5) - 0.05
            alpha_ci_high = growth_analysis.get("estimated_exponent", 0.5) + 0.05

        # Determine growth rate category
        estimated_exponent = growth_analysis.get("estimated_exponent", 0.5)
        if estimated_exponent < 0.4:
            growth_rate = "sublinear_slow"
        elif estimated_exponent < 0.6:
            growth_rate = "square_root"
        elif estimated_exponent < 0.9:
            growth_rate = "sublinear_fast"
        elif estimated_exponent < 1.1:
            growth_rate = "linear"
        else:
            growth_rate = "superlinear"

        return {
            "mistake_rate": mistake_rate,
            "ethical_primes_count": len(primes),
            "analysis": {
                "estimated_exponent": estimated_exponent,
                "alpha_ci_low": alpha_ci_low,
                "alpha_ci_high": alpha_ci_high,
                "erh_satisfied": growth_analysis.get("erh_satisfied", False),
                "r_squared": growth_analysis.get("r_squared", 0.0),
                "growth_rate": growth_rate,
            },
            "config": {
                "num_actions": num_actions,
                "complexity_dist": complexity_dist,
                "tau": tau,
            },
        }

    except Exception as e:
        logger.error(f"Error running simulation: {e}", exc_info=True)
        raise RuntimeError(f"Simulation failed: {str(e)}")


def save_simulation_results(
    results: Dict[str, Any],
    output_dir: Path,
    simulation_id: Optional[int] = None,
) -> str:
    """
    Save simulation results to disk.

    Args:
        results: Simulation results dictionary
        output_dir: Directory to save results
        simulation_id: Optional simulation ID for filename

    Returns:
        Path to saved results file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if simulation_id:
        filename = f"sim_result_{simulation_id}.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sim_result_{timestamp}.json"

    filepath = output_dir / filename

    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)

    return str(filepath)

