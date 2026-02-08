#!/usr/bin/env python3
"""
Comprehensive Report Generator
Aggregates JSON simulation results and generates a summary report + visualizations.
Includes Ethical Viability Score (EVS) and EVS over Time subfigure.
"""

import argparse
import json
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

try:
    from erh_core.analysis.statistics import calculate_evs
except ImportError:
    from simulation.analysis.statistics import calculate_evs


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
    if "estimated_exponent" in df.columns and df["estimated_exponent"].notna().any():
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x="complexity_dist", y="estimated_exponent")
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

def generate_markdown_report(df, output_dir):
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
        f.write(stats.to_markdown())
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

    print(f"Report generated at {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate Comprehensive Report")
    parser.add_argument("--input-dir", required=True, help="Directory containing JSON results")
    parser.add_argument("--output-dir", default="report", help="Output directory for report")
    
    args = parser.parse_args()
    
    df = load_results(args.input_dir)
    
    if df.empty:
        print("No data found.")
        return
        
    generate_visualizations(df, args.output_dir)
    generate_markdown_report(df, args.output_dir)

if __name__ == "__main__":
    main()
