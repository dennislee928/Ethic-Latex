#!/usr/bin/env python3
"""
ERH Real-World Data Integration Pipeline.

Processes empirical datasets (GitHub, COMPAS), computes alpha values,
and generates the empirical comparison plot for the LaTeX paper.

Usage:
  python scripts/run_empirical_data_pipeline.py [--output-dir simulation/output]

Outputs:
  - simulation/output/github_error_rates.json
  - simulation/output/compas_error_rates.json
  - simulation/output/figures/empirical_comparison.png
  - Updated real_world_results.json with github alpha
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _setup_paths() -> None:
    erh = PROJECT_ROOT / "erh_core"
    if erh.exists() and str(erh) not in sys.path:
        sys.path.insert(0, str(erh))


def _run_synthetic_radical() -> dict:
    """Run Radical judge simulation, return error comparison dict."""
    try:
        from erh_core.core.action_space import generate_world
        from erh_core.core.judgement_system import RadicalJudge, batch_evaluate
        from erh_core.core.ethical_primes import compare_error_distributions
    except ImportError:
        try:
            from simulation.core.action_space import generate_world
            from simulation.core.judgement_system import RadicalJudge, batch_evaluate
            from erh_core.core.ethical_primes import compare_error_distributions
        except ImportError:
            return {}

    actions = generate_world(
        num_actions=1000,
        complexity_dist="zipf",
        complexity_range=(1, 100),
        moral_ambiguity_factor=0.3,
        random_seed=42,
    )
    judges = {"Radical": RadicalJudge(amplification=1.5)}
    results = batch_evaluate(actions, judges, tau=0.3)
    return compare_error_distributions(results, X_max=100)


def main() -> int:
    parser = argparse.ArgumentParser(description="ERH empirical data pipeline")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "simulation" / "output",
        help="Output directory for JSON and figures",
    )
    args = parser.parse_args()

    _setup_paths()
    output_dir = args.output_dir.resolve()
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("ERH Real-World Data Integration Pipeline")
    print("=" * 60)

    # 1. Process GitHub
    print("\n[1/4] Processing GitHub PR data...")
    try:
        from simulation.real_data.process_github import process_github

        github_path = output_dir / "github_pr_empirical.json"
        github_json = PROJECT_ROOT / "data" / "empirical" / "github_pr_empirical.json"
        if not github_json.exists():
            github_json = PROJECT_ROOT / "data" / "github_pr_empirical.json"
        github_results = process_github(
            json_path=github_json if github_json.exists() else None,
            output_path=output_dir / "github_error_rates.json",
            use_stub_if_empty=True,
        )
        if "error" in github_results:
            print(f"  Warning: {github_results['error']}")
        else:
            print(f"  GitHub: α ≈ {github_results['alpha']:.4f} (n={github_results.get('n_prs', '?')})")
    except ImportError as e:
        print(f"  Error: {e}")
        github_results = {"error": str(e)}

    # 2. Process COMPAS
    print("\n[2/4] Processing COMPAS data...")
    try:
        from simulation.real_data.process_compas import process_compas

        compas_results = process_compas(output_path=output_dir / "compas_error_rates.json")
        if "error" in compas_results:
            print(f"  Warning: {compas_results['error']}")
        else:
            print(f"  COMPAS: α ≈ {compas_results['alpha']:.4f}")
    except ImportError as e:
        print(f"  Error: {e}")
        compas_results = {"error": str(e)}

    # 3. Run Radical simulation
    print("\n[3/4] Running Radical simulation...")
    error_comparison = _run_synthetic_radical()
    if error_comparison:
        print(f"  Radical simulation complete")
    else:
        print("  Warning: Could not run Radical simulation")

    # 4. Process HuggingFace + LLM (optional, uses free local DistilGPT-2)
    print("\n[4/6] Processing HuggingFace + LLM (Moral Stories)...")
    hf_results = {"error": "not run"}
    try:
        from simulation.real_data.process_huggingface_llm import process_huggingface_llm

        hf_results = process_huggingface_llm(
            dataset="moral_stories",
            max_samples=30,
            model_name="distilgpt2",
            output_path=output_dir / "huggingface_llm_error_rates.json",
        )
        if "error" in hf_results:
            print(f"  Warning: {hf_results['error']}")
        else:
            print(f"  HuggingFace LLM: α ≈ {hf_results['alpha']:.4f} (acc={hf_results.get('accuracy', 0):.1%}, model={hf_results.get('model_used', '?')})")
    except Exception as e:
        print(f"  Skipped: {e}")
        hf_results = {"error": str(e)}

    # 5. Generate plot
    print("\n[5/6] Generating empirical comparison plot...")
    try:
        import matplotlib
        matplotlib.use("Agg")
        from simulation.visualization.plots import plot_empirical_comparison

        fig_path = figures_dir / "empirical_comparison.png"
        hf_for_plot = hf_results if "error" not in hf_results else None
        plot_empirical_comparison(
            error_comparison=error_comparison if error_comparison else None,
            compas_results=compas_results if "error" not in compas_results else None,
            github_results=github_results if "error" not in github_results else None,
            huggingface_results=hf_for_plot,
            save_path=str(fig_path),
            show=False,
        )
        print(f"  Saved: {fig_path}")
    except ImportError as e:
        print(f"  Warning: Could not generate plot ({e})")

    # 6. Update real_world_results.json with github and huggingface
    rwr_path = output_dir / "real_world_results.json"
    try:
        rwr = {}
        if rwr_path.exists():
            with open(rwr_path, encoding="utf-8") as f:
                rwr = json.load(f)
        if "error" not in github_results:
            rwr.setdefault("github", {})
            rwr["github"]["alpha"] = github_results.get("alpha")
            rwr["github"]["n_prs"] = github_results.get("n_prs")
        if "error" not in hf_results:
            rwr.setdefault("huggingface_llm", {})
            rwr["huggingface_llm"]["alpha"] = hf_results.get("alpha")
            rwr["huggingface_llm"]["accuracy"] = hf_results.get("accuracy")
            rwr["huggingface_llm"]["model_used"] = hf_results.get("model_used")
        if rwr:
            with open(rwr_path, "w", encoding="utf-8") as f:
                json.dump(rwr, f, indent=2)
            print(f"\n  Updated {rwr_path}")
    except (json.JSONDecodeError, IOError):
        pass

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    print("  - github_error_rates.json")
    print("  - compas_error_rates.json")
    print("  - huggingface_llm_error_rates.json")
    print("  - figures/empirical_comparison.png")
    print("\nFor real LLM (DistilGPT-2): pip install transformers torch")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
