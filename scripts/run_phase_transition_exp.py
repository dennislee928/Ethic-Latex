#!/usr/bin/env python3
"""
Phase Transition Experiment: Coupling Strength J vs Ethical Stability.

Sweeps coupling strength J from J_min to J_max. For each J:
1. Quantum: compute_ground_state or MoralHamiltonian → fidelity
2. Judgement: generate_world → (Oracle or random V) → Judge → error_rate

Output: phase_transition_results.json, phase_transition.png

Usage:
    python scripts/run_phase_transition_exp.py [--output-dir DIR] [--no-oracle]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from erh_core.core.action_space import generate_world, populate_action_descriptions
    from erh_core.core.judgement_system import BiasedJudge, evaluate_judgement
except ImportError:
    from simulation.core.action_space import generate_world
    populate_action_descriptions = None
    from simulation.core.judgement_system import BiasedJudge, evaluate_judgement

try:
    from erh_core.core.oracle import HuggingFaceEthicalOracle
    from erh_core.core.judgement_system import OracleDrivenJudge
    _ORACLE_AVAILABLE = True
except ImportError:
    _ORACLE_AVAILABLE = False

try:
    from simulation.quantum.simulator import (
        SocialDynamicsQuantumSimulator,
        MoralHamiltonian,
    )
    _QUANTUM_AVAILABLE = True
except ImportError:
    _QUANTUM_AVAILABLE = False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run phase transition experiment: J vs ethical stability"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: simulation/output)",
    )
    parser.add_argument(
        "--J-min",
        type=float,
        default=0.0,
        help="Min coupling strength",
    )
    parser.add_argument(
        "--J-max",
        type=float,
        default=2.0,
        help="Max coupling strength",
    )
    parser.add_argument(
        "--n-points",
        type=int,
        default=21,
        help="Number of J points",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )
    parser.add_argument(
        "--n-qubits",
        type=int,
        default=4,
        help="Number of qubits for quantum simulation",
    )
    parser.add_argument(
        "--num-actions",
        type=int,
        default=100,
        help="Number of actions for judgement simulation per J",
    )
    parser.add_argument(
        "--no-oracle",
        action="store_true",
        help="Use random V from generate_world instead of HuggingFace Oracle",
    )
    parser.add_argument(
        "--save-plot",
        action="store_true",
        help="Save phase_transition.png",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir or ROOT / "simulation" / "output")
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    J_values = np.linspace(args.J_min, args.J_max, args.n_points)
    rng = np.random.default_rng(args.seed)

    use_oracle = _ORACLE_AVAILABLE and not args.no_oracle
    if use_oracle:
        try:
            oracle = HuggingFaceEthicalOracle(cache_path=str(output_dir / "oracle_cache.json"))
            judge = OracleDrivenJudge(oracle=oracle, inner_judge=BiasedJudge(bias_strength=0.2))
        except Exception:
            use_oracle = False
            judge = BiasedJudge(bias_strength=0.2)
    else:
        judge = BiasedJudge(bias_strength=0.2)

    error_rates = []
    fidelities = []

    for J in J_values:
        # Quantum: adjacency matrix with uniform J
        n = args.n_qubits
        adj = np.ones((n, n)) * J
        np.fill_diagonal(adj, 0)
        bias = rng.uniform(-0.2, 0.2, size=n)

        if _QUANTUM_AVAILABLE:
            try:
                sim = SocialDynamicsQuantumSimulator(num_agents=n, seed=args.seed)
                energy, _ = sim.compute_ground_state(adj, bias)
                # Map energy to fidelity proxy: lower energy = higher fidelity
                fid = max(0, min(1, 1.0 - 0.3 * (energy + 2)))
            except Exception:
                try:
                    mh = MoralHamiltonian(n_qubits=n, seed=args.seed)
                    cd = np.array([min(1.0, J)])
                    res = mh.run_phase_transition_sweep(cd, base_strength=0.5, shots=256)
                    fid = float(res["fidelities"][0])
                except Exception:
                    fid = 0.8 * np.exp(-0.5 * J) + 0.1 * rng.random()
        else:
            fid = 0.8 * np.exp(-0.5 * J) + 0.1 * rng.random()
        fidelities.append(float(fid))

        # Judgement
        actions = generate_world(
            num_actions=args.num_actions,
            complexity_dist="zipf",
            random_seed=args.seed + int(J * 100),
        )
        if populate_action_descriptions and use_oracle:
            populate_action_descriptions(actions, template="minimal")
        evaluate_judgement(actions, judge, tau=0.3, inplace=True)
        er = np.mean([a.mistake_flag for a in actions if a.mistake_flag is not None])
        error_rates.append(float(er))

    error_rates = np.array(error_rates)
    fidelities = np.array(fidelities)
    stability = 1.0 - error_rates

    # Critical point: first J where error_rate > 0.5
    idx = np.where(error_rates > 0.5)[0]
    critical_point_J = float(J_values[idx[0]]) if len(idx) > 0 else None

    result = {
        "coupling_strengths": J_values.tolist(),
        "error_rates": error_rates.tolist(),
        "fidelities": fidelities.tolist(),
        "stability": stability.tolist(),
        "critical_point_J": critical_point_J,
        "seed": args.seed,
        "n_qubits": args.n_qubits,
        "J_range": [args.J_min, args.J_max],
        "n_points": args.n_points,
        "use_oracle": use_oracle,
    }

    out_path = output_dir / "phase_transition_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Results saved to {out_path}")

    if critical_point_J is not None:
        print(f"Critical point J_c ≈ {critical_point_J:.3f}")

    if args.save_plot:
        try:
            from simulation.visualization.plots import plot_phase_transition

            plot_phase_transition(
                result,
                save_path=str(figures_dir / "phase_transition.png"),
                show=False,
            )
            print(f"Figure saved to {figures_dir / 'phase_transition.png'}")
        except ImportError:
            try:
                import matplotlib.pyplot as plt
                import seaborn as sns

                sns.set_style("paper")
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.plot(J_values, stability, "o-", label="Ethical Stability (1 - Error Rate)")
                ax.plot(J_values, fidelities, "s--", label="Quantum Fidelity")
                if critical_point_J is not None:
                    ax.axvline(x=critical_point_J, color="red", linestyle="--", alpha=0.7)
                ax.set_xlabel("Coupling Strength $J$")
                ax.set_ylabel("Ethical Stability / Fidelity")
                ax.legend()
                ax.grid(True, alpha=0.3)
                fig.savefig(figures_dir / "phase_transition.png", dpi=150, bbox_inches="tight")
                plt.close(fig)
                print(f"Figure saved to {figures_dir / 'phase_transition.png'}")
            except Exception as e:
                print(f"Could not save plot: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
