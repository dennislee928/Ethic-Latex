"""
Cross-case ERH comparison for real-world case studies.

Runs or accepts the five real-world cases from docs/erh_real_world_implementation.md
and produces an alpha-ranked table plus an optional bar chart.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "simulation" / "output" / "erh_case_comparison.json"
DEFAULT_OUTPUT_PNG = PROJECT_ROOT / "simulation" / "output" / "erh_case_alpha_comparison.png"


def _entry(name: str, result: Dict[str, Any]) -> Dict[str, Any] | None:
    if "alpha" not in result:
        return None
    return {
        "name": name,
        "alpha": float(result.get("alpha", 0.0)),
        "erh_satisfied": bool(result.get("erh_satisfied", False)),
        "mistake_rate": float(result.get("mistake_rate", 0.0)),
        "n_total": int(result.get("n_total", 0)),
    }


def _flatten_results(results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for case_name, result in results.items():
        if not isinstance(result, dict) or "error" in result:
            continue

        if isinstance(result.get("groups"), dict):
            for group_name, group_result in result["groups"].items():
                item = _entry(f"{case_name}:{group_name}", group_result)
                if item:
                    entries.append(item)
            continue

        if isinstance(result.get("pairs"), dict):
            for pair_name, pair_result in result["pairs"].items():
                item = _entry(f"{case_name}:{pair_name}", pair_result)
                if item:
                    entries.append(item)
            continue

        item = _entry(case_name, result)
        if item:
            entries.append(item)

    entries.sort(key=lambda item: item["alpha"], reverse=True)
    return entries


def _write_json(path: Path, summary: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def _write_bar_chart(path: Path, entries: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("matplotlib is required to generate ERH comparison charts") from exc

    rows = list(entries)
    names = [row["name"] for row in rows]
    alphas = [row["alpha"] for row in rows]
    colors = ["#c43c39" if alpha >= 0.6 else "#2f7d55" for alpha in alphas]

    width = max(7, len(rows) * 1.2)
    _, ax = plt.subplots(figsize=(width, 4.5))
    ax.bar(names, alphas, color=colors)
    ax.axhline(0.6, color="#333333", linestyle="--", linewidth=1, label="ERH threshold")
    ax.set_ylabel("alpha")
    ax.set_title("ERH alpha comparison across real-world cases")
    ax.tick_params(axis="x", labelrotation=35)
    ax.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def build_case_comparison(
    results: Dict[str, Dict[str, Any]],
    output_json: Path | None = None,
    output_png: Path | None = None,
) -> Dict[str, Any]:
    entries = _flatten_results(results)
    summary = {
        "case_name": "erh_case_comparison",
        "n_entries": len(entries),
        "entries": entries,
    }

    if output_json is not None:
        _write_json(output_json, summary)
    if output_png is not None:
        _write_bar_chart(output_png, entries)
    return summary


def _demo_compas_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "race": ["Black", "Black", "White", "White", "Black", "White"],
            "two_year_recid": [1, 0, 1, 0, 1, 0],
            "decile_score": [9, 3, 8, 2, 7, 4],
            "priors_count": [5, 0, 2, 1, 8, 0],
            "c_charge_degree": ["F", "M", "F", "M", "F", "M"],
            "days_b_screening_arrest": [10, 0, 8, 1, 30, 2],
        }
    )


def run_all_case_comparisons(
    output_json: Path | None = DEFAULT_OUTPUT_JSON,
    output_png: Path | None = DEFAULT_OUTPUT_PNG,
) -> Dict[str, Any]:
    from simulation.real_data.compas_case_study import run_compas_by_race
    from simulation.real_data.content_moderation_case_study import run_content_moderation_erh_analysis
    from simulation.real_data.llm_bias_case_study import run_llm_bias_erh_analysis
    from simulation.real_data.medical_triage_case_study import run_medical_triage_erh_analysis
    from simulation.real_data.truthfulqa_case_study import run_truthfulqa_erh_analysis

    compas_result = run_compas_by_race()
    if "error" in compas_result:
        compas_result = run_compas_by_race(_demo_compas_frame())

    results = {
        "content_moderation": run_content_moderation_erh_analysis(),
        "compas_by_race": compas_result,
        "medical_triage": run_medical_triage_erh_analysis(),
        "truthfulqa": run_truthfulqa_erh_analysis(max_samples=25),
        "llm_bias": run_llm_bias_erh_analysis(),
    }
    return build_case_comparison(results, output_json=output_json, output_png=output_png)


if __name__ == "__main__":  # pragma: no cover
    summary = run_all_case_comparisons()
    print(f"Compared {summary['n_entries']} ERH case entries")
    for entry in summary["entries"]:
        print(f"  {entry['name']}: alpha={entry['alpha']:.4f}, ERH={entry['erh_satisfied']}")
