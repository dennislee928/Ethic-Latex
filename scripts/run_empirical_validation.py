#!/usr/bin/env python3
"""
Run empirical validation on COMPAS and Adult Income datasets.

Computes ERH-style alpha values and saves results to simulation/output/real_world_results.json.
Prints alpha values to stdout for quick verification.

Usage:
    python scripts/run_empirical_validation.py [--output OUTPUT_PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

_np_ok = False
try:
    __import__("numpy")
    _np_ok = True
except ImportError:
    pass

# Auto-re-exec with project venv if numpy unavailable (user ran without activating venv)
if not _np_ok:
    for _venv in (PROJECT_ROOT / ".venv_erh", PROJECT_ROOT / ".venv"):
        _venv_py = _venv / "bin" / "python"
        if _venv_py.exists():
            os.execv(str(_venv_py), [str(_venv_py), __file__] + sys.argv[1:])
    print("ERROR: numpy not found. Activate the venv and install deps:\n  source .venv_erh/bin/activate\n  pip install -r requirements.txt\nOr run: .venv_erh/bin/python scripts/run_empirical_validation.py", file=sys.stderr)
    sys.exit(1)
DEFAULT_OUTPUT = PROJECT_ROOT / "simulation" / "output" / "real_world_results.json"


def _setup_paths() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    erh = PROJECT_ROOT / "erh_core"
    if erh.exists() and str(erh) not in sys.path:
        sys.path.insert(0, str(erh))


def run_synthetic_alphas() -> dict:
    """Compute alpha for Radical and Conservative judges (synthetic)."""
    result = {}
    try:
        from simulation.core.action_space import generate_world
        from simulation.core.judgement_system import (
            ConservativeJudge,
            RadicalJudge,
            batch_evaluate,
        )
        from simulation.analysis.statistics import compare_judges
    except ImportError:
        try:
            from erh_core.core.action_space import generate_world
            from erh_core.core.judgement_system import (
                ConservativeJudge,
                RadicalJudge,
                batch_evaluate,
            )
            from erh_core.analysis.statistics import compare_judges
        except ImportError:
            return result

    for name, judge_cls, kwargs in [
        ("Radical", RadicalJudge, {"amplification": 1.5}),
        ("Conservative", ConservativeJudge, {"threshold": 0.5}),
    ]:
        try:
            actions = generate_world(
                num_actions=1000,
                complexity_dist="zipf",
                complexity_range=(1, 100),
                random_seed=42,
            )
            judges = {name: judge_cls(**kwargs)}
            results = batch_evaluate(actions, judges, tau=0.3)
            comparison = compare_judges(results, X_max=100)
            if name in comparison and "error" not in comparison[name]:
                result[name] = {"alpha": float(comparison[name]["estimated_exponent"])}
        except Exception as e:
            result[name] = {"error": str(e)}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run empirical validation (COMPAS, Adult)")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSON path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    _setup_paths()

    results = {
        "compas": {},
        "adult": {},
        "synthetic": {},
    }

    # COMPAS
    try:
        from simulation.real_data.compas_case_study import run_compas_erh_analysis

        compas = run_compas_erh_analysis()
        results["compas"] = compas
        if "alpha" in compas:
            print(f"COMPAS α ≈ {compas['alpha']:.4f}")
        elif "error" in compas:
            print(f"COMPAS: {compas['error']}")
    except ImportError as e:
        results["compas"] = {"error": str(e)}
        print(f"COMPAS: import error - {e}")

    # Adult
    try:
        from simulation.real_data.adult_income_case_study import run_adult_erh_analysis

        adult = run_adult_erh_analysis()
        results["adult"] = adult
        if "alpha" in adult:
            print(f"Adult α ≈ {adult['alpha']:.4f}")
        elif "error" in adult:
            print(f"Adult: {adult['error']}")
    except ImportError as e:
        results["adult"] = {"error": str(e)}
        print(f"Adult: import error - {e}")

    # Synthetic (Radical, Conservative)
    synthetic = run_synthetic_alphas()
    results["synthetic"] = synthetic
    for name, data in synthetic.items():
        if "alpha" in data:
            print(f"Synthetic {name} α ≈ {data['alpha']:.4f}")
        elif "error" in data:
            print(f"Synthetic {name}: {data['error']}")

    # Save
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
