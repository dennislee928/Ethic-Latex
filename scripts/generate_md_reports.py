"""
Generate consolidated Markdown reports from simulation outputs.

This script is intended to be run in CI/CD pipelines as well as locally.
It collects relevant .md and .txt reports produced by simulations and tests
and concatenates them into a single Markdown file under docs/.

Design goals:
- Be safe to run even when some source files are missing (no hard failures).
- Avoid any network access or heavy computation.
- Provide a single, human-readable summary artifact for experiments.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIM_OUTPUT = PROJECT_ROOT / "simulation" / "output"
PSYCH_OUTPUT = SIM_OUTPUT / "psychohistory_tests"
TESTS_DIR = PROJECT_ROOT / "tests"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_MD = DOCS_DIR / "EXPERIMENT_REPORTS.md"


def _collect_existing(paths: Iterable[Path]) -> List[Path]:
    files: List[Path] = []
    for p in paths:
        if p.exists() and p.is_file():
            files.append(p)
    return files


def generate_markdown_report(output_path: Path = OUTPUT_MD) -> None:
    """
    Concatenate available experiment-related Markdown / text reports into a
    single Markdown file. Missing files are silently ignored.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    candidates = [
        SIM_OUTPUT / "judge_comparison_report.md",
        SIM_OUTPUT / "results_summary.txt",
        SIM_OUTPUT / "real_data_case_study_report.md",
        SIM_OUTPUT / "exam_cheating_case_study_report.md",
        SIM_OUTPUT / "sexual_abuse_case_study_report.md",
        SIM_OUTPUT / "alpha_stability_report.md",
        PSYCH_OUTPUT / "test_summary.txt",
        TESTS_DIR / "PSYCHOHISTORY_TESTS_README.md",
    ]

    files = _collect_existing(candidates)

    lines: List[str] = []
    lines.append("# Experiment and Test Reports\n")
    lines.append(
        "This document aggregates selected reports produced by the ERH "
        "simulation framework, real-data case studies, and psychohistory "
        "integration tests.\n"
    )
    lines.append(
        "In the summary tables, the column **Within ERH-style bound?** refers to "
        "whether the estimated growth exponent $\\alpha$ stays at or below an "
        "ERH-style worst-case target (roughly $\\alpha \\approx 0.5$). A \"No\" "
        "entry in these tables indicates that the system's error grows *more "
        "slowly* than the worst-case bound (i.e., it is overly conservative), "
        "not that it explodes beyond the bound.\n"
    )

    if not files:
        lines.append("_No report files were found. Run simulations and tests "
                     "locally to populate simulation/output/ before calling "
                     "this script._\n")
    else:
        for f in files:
            rel = f.relative_to(PROJECT_ROOT)
            lines.append(f"\n---\n\n## {rel.as_posix()}\n\n")
            try:
                content = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = f.read_text(errors="replace", encoding="utf-8")
            lines.append(content.strip() + "\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[generate_md_reports] Wrote consolidated report to {output_path}")


if __name__ == "__main__":  # pragma: no cover
    generate_markdown_report()


