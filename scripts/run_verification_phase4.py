#!/usr/bin/env python3
"""
Phase 4 Verification: End-to-end pipeline check.

Runs a minimal verification that:
1. Simulation batch produces JSON output
2. Phase transition experiment produces figure
3. Generate comprehensive report runs
4. (Optional) generate_all_figures produces comparison table

Usage:
    python scripts/run_verification_phase4.py [--full]
    --full: also run generate_all_figures (slower)
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], desc: str) -> bool:
    """Run command, return True on success."""
    print(f"\n[{desc}]")
    print("  " + " ".join(cmd))
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env={**dict(__import__("os").environ), "PYTHONPATH": f"{ROOT}:{ROOT}/erh_core"},
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        print(f"  FAIL (exit {result.returncode})")
        if result.stderr:
            print("  stderr:", result.stderr[:500])
        return False
    print("  OK")
    return True


def main():
    parser = argparse.ArgumentParser(description="Phase 4 end-to-end verification")
    parser.add_argument("--full", action="store_true", help="Also run generate_all_figures")
    args = parser.parse_args()

    out = ROOT / "simulation" / "output"
    out.mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(exist_ok=True)
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    errors = []

    # 1. Simulation batch (minimal: 1 instance, 50 actions)
    if not run(
        [
            sys.executable,
            "scripts/run_simulation_batch.py",
            "--num-actions",
            "50",
            "--output-dir",
            str(results_dir),
            "--instances",
            "1",
        ],
        "1. Simulation batch",
    ):
        errors.append("Simulation batch failed")

    # 2. Phase transition experiment
    if not run(
        [
            sys.executable,
            "scripts/run_phase_transition_exp.py",
            "--no-oracle",
            "--save-plot",
            "--output-dir",
            str(out),
            "--n-points",
            "5",
        ],
        "2. Phase transition experiment",
    ):
        errors.append("Phase transition failed")

    # 3. Generate comprehensive report
    if not run(
        [
            sys.executable,
            "scripts/generate_comprehensive_report.py",
            "--input-dir",
            str(results_dir),
            "--output-dir",
            str(ROOT / "final_report"),
        ],
        "3. Generate comprehensive report",
    ):
        errors.append("Generate report failed")

    # 4. (Optional) Generate all figures
    if args.full:
        if not run(
            [sys.executable, "-m", "simulation.generate_all_figures"],
            "4. Generate all figures",
        ):
            errors.append("Generate all figures failed")
    else:
        print("\n[4. Generate all figures] SKIPPED (use --full to run)")

    # Verify outputs exist
    phase_png = out / "figures" / "phase_transition.png"
    pt_json = out / "phase_transition_results.json"
    if not phase_png.exists():
        errors.append(f"Missing {phase_png}")
    if not pt_json.exists():
        errors.append(f"Missing {pt_json}")

    if errors:
        print("\n" + "=" * 50)
        print("VERIFICATION FAILED")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Phase 4 verification PASSED")
    print(f"  - {phase_png}")
    print(f"  - {pt_json}")
    sys.exit(0)


if __name__ == "__main__":
    main()
