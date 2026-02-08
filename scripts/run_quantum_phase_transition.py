#!/usr/bin/env python3
"""
Quantum Phase Transition Experiment for Ethical Riemann Hypothesis.

Runs MoralHamiltonian with increasing conflict density and measures:
- Von Neumann entropy (or coherence proxy)
- Ground state fidelity
- Collapse point (phase transition at x_crit)

Hypothesis: When conflict (complexity) exceeds a threshold, the system
cannot reach a stable ground state → fidelity drops → "Pole" of the
Ethical Zeta Function.

Usage:
    python scripts/run_quantum_phase_transition.py [--output-dir OUTPUT_DIR]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

# Add project root for imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from simulation.quantum.simulator import MoralHamiltonian
except ImportError:
    MoralHamiltonian = None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run quantum phase transition experiment for ERH"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory for JSON results and figures (default: simulation/output)",
    )
    parser.add_argument(
        "--n-qubits",
        type=int,
        default=4,
        help="Number of qubits (principles)",
    )
    parser.add_argument(
        "--n-points",
        type=int,
        default=20,
        help="Number of conflict density points",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )
    parser.add_argument(
        "--save-plot",
        action="store_true",
        help="Save phase transition plot to output dir",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    if output_dir is None:
        output_dir = ROOT / "simulation" / "output"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if MoralHamiltonian is None:
        print("Warning: MoralHamiltonian not available (qiskit missing). Using mock.")
        result = _mock_run(args.n_points, args.seed)
    else:
        conflict_densities = np.linspace(0.05, 1.0, args.n_points)
        mh = MoralHamiltonian(n_qubits=args.n_qubits, seed=args.seed)
        result = mh.run_phase_transition_sweep(
            conflict_densities=conflict_densities,
            base_strength=0.5,
            shots=2048,
        )

    # Output JSON
    out_path = output_dir / "quantum_phase_transition_results.json"
    serializable = {
        "conflict_densities": result["conflict_densities"].tolist(),
        "fidelities": result["fidelities"].tolist(),
        "coherences": result["coherences"].tolist(),
        "collapse_point": result.get("collapse_point"),
        "n_qubits": args.n_qubits,
        "seed": args.seed,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)
    print(f"Results saved to {out_path}")

    if result.get("collapse_point") is not None:
        print(f"Estimated collapse point (x_crit): {result['collapse_point']:.3f}")

    if args.save_plot:
        try:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(8, 5))
            x = result["conflict_densities"]
            ax.plot(x, result["fidelities"], "o-", label="Ground State Fidelity")
            ax.plot(x, result["coherences"], "s--", label="Consensus Coherence")
            ax.axhline(y=0.3, color="gray", linestyle=":", alpha=0.7)
            if result.get("collapse_point") is not None:
                ax.axvline(
                    x=result["collapse_point"],
                    color="red",
                    linestyle="--",
                    alpha=0.7,
                    label=f"Collapse point ≈ {result['collapse_point']:.2f}",
                )
            ax.set_xlabel("Conflict Density (Complexity)")
            ax.set_ylabel("Fidelity / Coherence")
            ax.set_title("Moral Phase Transition: Ethical Conflict → Spin Glass Frustration")
            ax.legend()
            ax.grid(True, alpha=0.3)
            fig_path = output_dir / "phase_transition_diagram.png"
            fig.savefig(fig_path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"Figure saved to {fig_path}")
        except ImportError:
            print("matplotlib not available; skipping plot save")

    return 0


def _mock_run(n_points: int, seed: int) -> dict:
    """Mock run when Qiskit is unavailable."""
    np.random.seed(seed)
    conflict_densities = np.linspace(0.05, 1.0, n_points)
    # Simulate fidelity decay with conflict
    fidelities = 0.8 * np.exp(-1.5 * conflict_densities) + 0.1 * np.random.rand(n_points)
    coherences = np.clip(fidelities + 0.1 * np.random.randn(n_points), 0, 1)
    idx = np.where(fidelities < 0.3)[0]
    collapse_point = float(conflict_densities[idx[0]]) if len(idx) > 0 else None
    return {
        "conflict_densities": conflict_densities,
        "fidelities": fidelities,
        "coherences": coherences,
        "collapse_point": collapse_point,
    }


if __name__ == "__main__":
    sys.exit(main())
