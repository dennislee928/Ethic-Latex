#!/usr/bin/env python3
"""
Comprehensive Report Generator
Aggregates JSON simulation results and generates a summary report + visualizations.
Includes Ethical Viability Score (EVS), EVS over Time, and phase transition figure.
Runs phase transition experiment at start to ensure phase_transition.png exists.
"""

import argparse
import json
import os
import glob
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_pandas_ok = False
try:
    __import__("pandas")
    _pandas_ok = True
except ImportError:
    pass

# Auto-re-exec with project venv if pandas unavailable
if not _pandas_ok:
    for _venv in (ROOT / ".venv_erh", ROOT / ".venv"):
        _venv_py = _venv / "bin" / "python"
        if _venv_py.exists():
            os.execv(str(_venv_py), [str(_venv_py), __file__] + sys.argv[1:])
    print("ERROR: pandas not found. Activate the venv and install deps:\n  source .venv_erh/bin/activate\n  pip install -r requirements.txt\nOr run: .venv_erh/bin/python scripts/generate_comprehensive_report.py ...", file=sys.stderr)
    sys.exit(1)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from erh_core.analysis.statistics import calculate_evs
except ImportError:
    from simulation.analysis.statistics import calculate_evs


def _generate_expand_plots(output_dir: str) -> None:
    """Generate expand.plan figures: normalized error, phase transition h, prime ladder, von Neumann entropy."""
    try:
        from simulation.visualization.plots import (
            plot_normalized_error_growth,
            plot_quantum_phase_transition,
            plot_prime_ladder,
            plot_von_neumann_entropy_over_time,
            plot_compas_erh_bound,
            plot_alpha_comparison_bar,
            plot_normalized_error_oscillation,
            plot_universal_error_growth,
        )
    except ImportError as e:
        print(f"Expand plots skipped (import error): {e}")
        return
    import numpy as np
    fig_dir = Path(output_dir) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Synthetic data for normalized error
    x = np.arange(2, 101, dtype=float)
    E_x = 0.5 * np.sqrt(x) * np.sin(2 * np.pi * np.log(x) / 3)
    plot_normalized_error_growth(x, E_x, save_path=str(fig_dir / "paper_fig9_normalized_oscillation.pdf"), show=False)

    # Phase transition h vs magnetization
    h_vals = np.linspace(0, 2, 30)
    mag = np.exp(-h_vals)  # Decay with h
    h_c = 1.0
    plot_quantum_phase_transition(h_vals, mag, critical_h=h_c, save_path=str(fig_dir / "paper_fig10_phase_transition_h.pdf"), show=False)

    # Prime ladder (step-like cumulative count)
    Pi_x = np.floor(np.log(x) * 8).astype(float)
    plot_prime_ladder(x, Pi_x, save_path=str(fig_dir / "paper_fig11_prime_ladder.pdf"), show=False)

    # Von Neumann entropy over time
    t = np.arange(0, 20)
    S = 0.3 + 0.4 * (1 - np.exp(-t / 5))
    plot_von_neumann_entropy_over_time(t, S, save_path=str(fig_dir / "von_neumann_entropy_over_time.pdf"), show=False)

    # Killer plots: COMPAS ERH bound, alpha comparison, normalized oscillation
    try:
        from simulation.real_data.compas_case_study import run_compas_erh_analysis
        from simulation.real_data.adult_income_case_study import run_adult_erh_analysis

        compas = run_compas_erh_analysis()
        adult = run_adult_erh_analysis()
        real_results = {"compas": compas, "adult": adult}

        if "error" not in compas:
            plot_compas_erh_bound(compas, save_path=str(fig_dir / "compas_erh_bound.png"), show=False)

        # Synthetic alpha for bar chart
        try:
            from simulation.core.action_space import generate_world
            from simulation.core.judgement_system import ConservativeJudge, RadicalJudge, batch_evaluate
            from simulation.analysis.statistics import compare_judges
        except ImportError:
            from erh_core.core.action_space import generate_world
            from erh_core.core.judgement_system import ConservativeJudge, RadicalJudge, batch_evaluate
            from erh_core.analysis.statistics import compare_judges

        synthetic = {}
        for name, cls, kw in [("Radical", RadicalJudge, {"amplification": 1.5}), ("Conservative", ConservativeJudge, {"threshold": 0.5})]:
            try:
                actions = generate_world(num_actions=1000, complexity_dist="zipf", random_seed=42)
                results = batch_evaluate(actions, {name: cls(**kw)}, tau=0.3)
                comp = compare_judges(results, X_max=100)
                if name in comp and "error" not in comp[name]:
                    synthetic[name] = {"alpha": float(comp[name]["estimated_exponent"])}
            except Exception:
                pass

        plot_alpha_comparison_bar(synthetic, real_results, save_path=str(fig_dir / "alpha_comparison_bar.png"), show=False)

        # Figure 6: Universal Error Growth Laws - simulated agents + COMPAS on same log-log plot
        try:
            from simulation.core.judgement_system import BiasedJudge
            from erh_core.core.ethical_primes import compare_error_distributions
        except ImportError:
            try:
                from erh_core.core.judgement_system import BiasedJudge
                from erh_core.core.ethical_primes import compare_error_distributions
            except ImportError:
                BiasedJudge = None
                compare_error_distributions = None
        if BiasedJudge is not None and compare_error_distributions is not None:
            try:
                actions = generate_world(num_actions=1000, complexity_dist="zipf", random_seed=42)
                sim_results = batch_evaluate(actions, {"Biased": BiasedJudge(bias_strength=0.2)}, tau=0.3)
                error_comparison = compare_error_distributions(sim_results, X_max=100)
                plot_universal_error_growth(
                    error_comparison, compas,
                    title="Universal Error Growth Laws",
                    save_path=str(fig_dir / "universal_error_growth.png"),
                    show=False,
                )
            except Exception as e:
                print(f"Universal error growth plot skipped: {e}")

        # Normalized oscillation with confidence interval
        if "error" not in compas and "x" in compas:
            xx = np.array(compas["x"])
            ee = np.array(compas["E_x"])
            plot_normalized_error_oscillation(
                xx, ee,
                confidence_interval=(-2.0, 2.0),
                save_path=str(fig_dir / "normalized_error_oscillation.png"),
                show=False,
            )
    except Exception as e:
        print(f"Killer plots skipped: {e}")


def run_phase_transition_exp(output_dir: str) -> bool:
    """Run phase transition experiment and save figure. Returns True on success."""
    try:
        script = ROOT / "scripts" / "run_phase_transition_exp.py"
        if not script.exists():
            return False
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [sys.executable, str(script), "--output-dir", str(out), "--no-oracle", "--save-plot"],
            cwd=str(ROOT),
            capture_output=True,
            timeout=300,
        )
        return result.returncode == 0
    except Exception:
        return False


def load_results(input_dir):
    """Load all JSON result files from input directory."""
    files = glob.glob(os.path.join(input_dir, "sim_result_*.json"))
    data = []

    print(f"Found {len(files)} result files in {input_dir}")

    for f in files:
        try:
            with open(f) as fh:
                res = json.load(fh)

            # Flatten structure
            row = {
                "filename": os.path.basename(f),
                "timestamp": res.get("timestamp"),
                "complexity_dist": res["config"]["complexity_dist"],
                "num_actions": res["config"]["num_actions"],
                "mistake_rate": res["metrics"]["mistake_rate"],
                "ethical_primes_count": res["metrics"]["ethical_primes_count"],
                "erh_satisfied": res["metrics"]["erh_satisfied"],
                "estimated_exponent": res["metrics"].get("estimated_exponent"),
            }
            data.append(row)
        except Exception as e:
            print(f"Error reading {f}: {e}")

    df = pd.DataFrame(data)
    if not df.empty:
        df = _add_evs_columns(df)
    return df


def _add_evs_columns(df):
    """Derive stability, fairness, polarization and EVS from metrics."""
    stability = 1.0 - df["mistake_rate"].fillna(0)
    # Fairness: exponent near 0.5 is ideal; 1 - 2*|α-0.5| ∈ [0,1]
    exp = df["estimated_exponent"].fillna(0.5)
    fairness = (1.0 - 2 * (exp - 0.5).abs()).clip(0, 1)
    polarization = 0.0  # Single-run; no polarization data
    df["stability"] = stability
    df["fairness"] = fairness
    df["polarization"] = polarization
    df["evs"] = df.apply(
        lambda r: calculate_evs(r["stability"], r["fairness"], r["polarization"]),
        axis=1,
    )
    return df


def generate_visualizations(df, output_dir):
    """Generate plots from aggregated data."""
    os.makedirs(output_dir, exist_ok=True)
    sns.set_theme(style="whitegrid")

    # 1. Mistake Rate by Complexity Distribution
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="complexity_dist", y="mistake_rate", errorbar="sd")
    plt.title("Mistake Rate by Complexity Distribution")
    plt.ylabel("Mistake Rate")
    plt.xlabel("Distribution")
    plt.savefig(os.path.join(output_dir, "mistake_rate_comparison.png"))
    plt.close()

    # 2. Alpha (Exponent) by Complexity Distribution
    # Use plt.boxplot with orientation='vertical' to avoid seaborn vert deprecation warning
    if "estimated_exponent" in df.columns and df["estimated_exponent"].notna().any():
        plt.figure(figsize=(10, 6))
        valid = df.dropna(subset=["estimated_exponent"])
        order = valid["complexity_dist"].unique()
        data = [valid[valid["complexity_dist"] == g]["estimated_exponent"].values for g in order]
        plt.boxplot(data, tick_labels=order.tolist(), patch_artist=True)
        plt.axhline(y=0.5, color="r", linestyle="--", label="ERH limit (0.5)")
        plt.title("Error Growth Exponent (α) Distribution")
        plt.ylabel("α (Exponent)")
        plt.legend()
        plt.savefig(os.path.join(output_dir, "alpha_comparison.png"))
        plt.close()

    # 3. EVS over Time / by run order
    if "evs" in df.columns:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # EVS over Time (run order)
        df_sorted = df.sort_values("timestamp", na_position="last").reset_index(drop=True)
        axes[0].plot(df_sorted.index, df_sorted["evs"], "o-", alpha=0.7)
        axes[0].set_xlabel("Run Index (chronological)")
        axes[0].set_ylabel("Ethical Viability Score (EVS)")
        axes[0].set_title("EVS over Time")
        axes[0].set_ylim(0, 1.05)
        axes[0].grid(True, alpha=0.3)

        # EVS by Complexity Distribution
        sns.barplot(data=df, x="complexity_dist", y="evs", errorbar="sd", ax=axes[1])
        axes[1].set_ylabel("Ethical Viability Score (EVS)")
        axes[1].set_xlabel("Distribution")
        axes[1].set_title("EVS by Complexity Distribution")
        axes[1].set_ylim(0, 1.05)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "evs_over_time.png"))
        plt.close()

def _append_empirical_section(f, empirical_dir: str) -> None:
    """Append Empirical Data section if data/empirical exists (HuggingFace, AITA, GitHub PR)."""
    emp_path = Path(empirical_dir) / "empirical"
    if not emp_path.exists():
        return
    summaries = []
    for name, fname in [
        ("HuggingFace", "huggingface_empirical.json"),
        ("Reddit AITA", "aita_empirical.json"),
        ("GitHub PR", "github_pr_empirical.json"),
    ]:
        p = emp_path / fname
        if p.exists():
            try:
                with open(p) as fp:
                    data = json.load(fp)
                err = data.get("error")
                if err:
                    summaries.append(f"- **{name}**: error: {err}")
                elif "count" in data:
                    summaries.append(f"- **{name}**: {data['count']} rows")
                elif "datasets" in data:
                    counts = [f"{k}={v.get('count', '?')}" for k, v in data.get("datasets", {}).items()]
                    summaries.append(f"- **{name}**: " + ", ".join(counts))
                else:
                    summaries.append(f"- **{name}**: fetched")
            except Exception as e:
                summaries.append(f"- **{name}**: read error: {e}")
    if summaries:
        f.write("\n## Empirical Data (Pipeline Fetch)\n")
        f.write("Real-world data sources used for ERH validation:\n\n")
        f.write("\n".join(summaries) + "\n\n")


def generate_markdown_report(df, output_dir, empirical_dir: str = ""):
    """Create a markdown summary report."""
    report_path = os.path.join(output_dir, "summary_report.md")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(report_path, "w") as f:
        f.write("# ERH Simulation Campaign Report\n")
        f.write(f"**Generated:** {timestamp}\n\n")

        f.write("## Overview\n")
        f.write(f"- Total Experiments: {len(df)}\n")
        f.write(f"- Distributions Tested: {', '.join(df['complexity_dist'].unique())}\n\n")

        f.write("## Aggregate Statistics\n")
        cols = ["mistake_rate", "estimated_exponent", "erh_satisfied"]
        if "evs" in df.columns:
            cols.append("evs")
        stats = df.groupby("complexity_dist")[cols].mean()
        try:
            f.write(stats.to_markdown())
        except ImportError:
            f.write(stats.to_string())
        f.write("\n\n")

        f.write("## ERH Compliance\n")
        compliance = df.groupby("complexity_dist")["erh_satisfied"].mean() * 100
        f.write("| Distribution | % Satisfied ERH |\n")
        f.write("|--------------|------------------|\n")
        for dist, rate in compliance.items():
            f.write(f"| {dist} | {rate:.1f}% |\n")
        f.write("\n")

        if "evs" in df.columns:
            f.write("## Ethical Viability Score (EVS)\n")
            evs_mean = df.groupby("complexity_dist")["evs"].mean()
            f.write("| Distribution | Mean EVS |\n")
            f.write("|--------------|----------|\n")
            for dist, evs in evs_mean.items():
                f.write(f"| {dist} | {evs:.3f} |\n")
            f.write("\n")

        f.write("## Visualizations\n")
        f.write("![Mistake Rate](mistake_rate_comparison.png)\n\n")
        f.write("![Alpha Comparison](alpha_comparison.png)\n\n")
        if "evs" in df.columns and os.path.isfile(os.path.join(output_dir, "evs_over_time.png")):
            f.write("![EVS over Time](evs_over_time.png)\n")

        if empirical_dir:
            _append_empirical_section(f, empirical_dir)

    print(f"Report generated at {report_path}")

def write_phase_transition_latex(output_dir: str) -> None:
    """Append phase_transition.png LaTeX snippet to figures_latex_code.tex if present."""
    fig_path = Path(output_dir) / "figures" / "phase_transition.png"
    tex_path = ROOT / "simulation" / "output" / "figures_latex_code.tex"
    if not fig_path.exists():
        return
    snippet = f"""
% Phase transition figure (from run_phase_transition_exp.py)
\\begin{{figure}}[htbp]
  \\centering
  \\includegraphics[width=0.85\\textwidth]{{figures/phase_transition.png}}
  \\caption{{Phase transition: Ethical stability vs coupling strength $J$. Critical point $J_c$ marked.}}
  \\label{{fig:phase_transition}}
\\end{{figure}}
"""
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = tex_path.read_text(encoding="utf-8") if tex_path.exists() else ""
        if "phase_transition" not in existing:
            with open(tex_path, "a", encoding="utf-8") as f:
                f.write(snippet)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Generate Comprehensive Report")
    parser.add_argument("--input-dir", required=True, help="Directory containing JSON results")
    parser.add_argument("--output-dir", default="report", help="Output directory for report")
    parser.add_argument("--empirical-dir", default="", help="Directory containing data/empirical (HuggingFace, AITA, GitHub PR)")
    parser.add_argument("--skip-phase-transition", action="store_true", help="Skip phase transition run")
    args = parser.parse_args()

    output_dir = args.output_dir
    sim_output = str(ROOT / "simulation" / "output")

    if not args.skip_phase_transition:
        print("Running phase transition experiment...")
        if run_phase_transition_exp(sim_output):
            print("Phase transition complete.")
        else:
            print("Phase transition skipped or failed.")
        write_phase_transition_latex(sim_output)
    print("Generating expand.plan figures...")
    _generate_expand_plots(sim_output)

    df = load_results(args.input_dir)

    if df.empty:
        print("No simulation data found; phase transition figure may still be available.")
        os.makedirs(output_dir, exist_ok=True)
        if (Path(sim_output) / "figures" / "phase_transition.png").exists():
            import shutil
            dest = Path(output_dir) / "phase_transition.png"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(Path(sim_output) / "figures" / "phase_transition.png", dest)
        return

    generate_visualizations(df, output_dir)
    generate_markdown_report(df, output_dir, empirical_dir=args.empirical_dir or str(ROOT / "data"))

if __name__ == "__main__":
    main()
