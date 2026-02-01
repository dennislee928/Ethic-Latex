#!/usr/bin/env python3
"""
Calculate Real World α vs Simulated Conservative α and generate comparison plot.

Phase 2: Scientific Grounding & Real Data.
Output: simulation/output/figures/alpha_comparison_real_vs_simulated.png
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "simulation" / "output" / "figures"
OUTPUT_PLOT = OUTPUT_DIR / "alpha_comparison_real_vs_simulated.png"


def _setup_paths() -> None:
    """Ensure project root is in path for simulation imports."""
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))


def _get_real_world_alphas() -> Dict[str, float]:
    """Compute alpha for Adult Income and COMPAS (if available)."""
    result: Dict[str, float] = {}
    try:
        from simulation.real_data.adult_income_case_study import compute_real_world_alpha

        alpha = compute_real_world_alpha()
        if alpha is not None:
            result["Adult Income"] = alpha
    except ImportError:
        pass
    try:
        from simulation.real_data.compas_case_study import run_compas_alpha

        alpha = run_compas_alpha()
        if alpha is not None:
            result["COMPAS"] = alpha
    except ImportError:
        pass
    return result


def _get_simulated_conservative_alpha(num_seeds: int = 10) -> float:
    """Run simulated Conservative judge, compute average alpha across seeds."""
    from simulation.core.action_space import generate_world
    from simulation.core.judgement_system import ConservativeJudge, batch_evaluate
    from simulation.analysis.statistics import compare_judges

    alphas: List[float] = []
    for seed in range(num_seeds):
        actions = generate_world(
            num_actions=1000,
            complexity_dist="zipf",
            complexity_range=(1, 100),
            moral_ambiguity_factor=0.3,
            random_seed=seed,
        )
        judges = {"Conservative": ConservativeJudge(threshold=0.5)}
        results = batch_evaluate(actions, judges, tau=0.3)
        comparison = compare_judges(results, X_max=100)
        if "Conservative" in comparison and "error" not in comparison["Conservative"]:
            alphas.append(float(comparison["Conservative"]["estimated_exponent"]))
    return float(np.mean(alphas)) if alphas else 0.0


def _generate_plot(
    real_alphas: Dict[str, float],
    simulated_alpha: float,
    output_path: Path,
) -> None:
    """Generate bar chart: Real World α vs Simulated Conservative α."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("[alpha_comparison] matplotlib not installed; skipping plot generation.")
        return

    labels: List[str] = []
    values: List[float] = []
    colors: List[str] = []

    for name, alpha in real_alphas.items():
        labels.append(f"Real: {name}")
        values.append(alpha)
        colors.append("#2ecc71")

    labels.append("Simulated: Conservative")
    values.append(simulated_alpha)
    colors.append("#3498db")

    fig, ax = plt.subplots(figsize=(8, 5))
    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, values, color=colors, edgecolor="black", linewidth=0.5)
    ax.axhline(y=0, color="gray", linestyle="-", linewidth=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylabel(r"Growth exponent $\alpha$")
    ax.set_title(r"Real World $\alpha$ vs Simulated Conservative $\alpha$ (ERH)")
    ax.legend(["Real data", "Simulated"], loc="upper right", fontsize=8)

    for bar, v in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + (0.02 if v >= 0 else -0.08),
            f"{v:.3f}",
            ha="center",
            va="bottom" if v >= 0 else "top",
            fontsize=10,
        )

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[alpha_comparison] Plot saved to {output_path}")


def main() -> None:
    _setup_paths()
    real_alphas = _get_real_world_alphas()
    simulated_alpha = _get_simulated_conservative_alpha()
    _generate_plot(real_alphas, simulated_alpha, OUTPUT_PLOT)


if __name__ == "__main__":
    main()
