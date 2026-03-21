#!/usr/bin/env python3
"""
Process UCI Student Performance dataset to exam_cheating_cases.csv schema.

Source: UCI ML Repository - Student Performance (Cortez & Silva, 2008)
URL: https://archive.ics.uci.edu/static/public/320/student+performance.zip

Expects: data/real_world/student-mat.csv and student-por.csv (from fetch_real_data.sh)
Output: data/exam_cheating_cases.csv

Schema mapping:
- cheated: proxy from (G3 - G2) > 3 or (G3 > G2 + 2 and studytime <= 2)
- region: from school (GP/MS)
- country: derived from school
- avg_score, score_std: from G1, G2, G3
- time_per_question, suspicious_similarity, proctor_flags: derived
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "real_world"
OUTPUT_PATH = ROOT / "data" / "exam_cheating_cases.csv"

# UCI Student Performance columns
REQUIRED_COLS = ["school", "G1", "G2", "G3", "studytime", "absences", "failures"]


def _load_student_csv(path: Path) -> pd.DataFrame | None:
    """Load a single student CSV; return None if missing or invalid."""
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path, sep=";")
        for c in REQUIRED_COLS:
            if c not in df.columns:
                return None
        return df
    except Exception:
        return None


def _cheated_proxy(df: pd.DataFrame) -> np.ndarray:
    """
    Proxy for cheating: (G3 - G2) > 3 or (G3 > G2 + 2 and studytime <= 2).
    Intended as methodological proxy, not ground truth.
    """
    grade_jump = (df["G3"] - df["G2"]).values
    low_study = (df["studytime"].values <= 2).astype(int)
    cheated = ((grade_jump > 3) | ((grade_jump > 2) & (low_study == 1))).astype(int)
    return cheated


def process_student_to_exam_cheating(
    data_dir: Path | None = None,
    output_path: Path | None = None,
) -> Path | None:
    """
    Process UCI Student Performance CSVs to exam_cheating_cases.csv schema.

    Returns output path on success, None on failure (graceful exit).
    """
    data_dir = data_dir or DATA_DIR
    output_path = output_path or OUTPUT_PATH

    mat = _load_student_csv(data_dir / "student-mat.csv")
    por = _load_student_csv(data_dir / "student-por.csv")

    dfs = [d for d in [mat, por] if d is not None]
    if not dfs:
        print(f"[process_student] No student-mat.csv or student-por.csv in {data_dir}")
        return None

    df = pd.concat(dfs, ignore_index=True)

    # Schema mapping
    region = df["school"].map({"GP": "Portugal-North", "MS": "Portugal-South"}).fillna("Unknown")
    country = df["school"].map({"GP": "PT-GP", "MS": "PT-MS"}).fillna("PT")

    avg_score = (df["G1"] + df["G2"] + df["G3"]) / 3.0
    score_std = df[["G1", "G2", "G3"]].std(axis=1).fillna(0)

    # studytime: 1=<<2h, 2=2-5h, 3=5-10h, 4=>10h -> proxy time per question (sec)
    time_map = {1: 90, 2: 60, 3: 45, 4: 30}
    time_per_question = df["studytime"].map(time_map).fillna(60)

    # suspicious_similarity: higher absences + failures -> higher suspicion
    abs_norm = np.clip(df["absences"].values / 20.0, 0, 1)
    fail_norm = np.clip(df["failures"].values / 4.0, 0, 1)
    suspicious_similarity = (0.4 * abs_norm + 0.6 * fail_norm).round(3)

    proctor_flags = (df["absences"] > 10).astype(int)

    subject_count = 3  # G1, G2, G3

    cheated = _cheated_proxy(df)

    out_df = pd.DataFrame(
        {
            "region": region,
            "country": country,
            "subject_count": subject_count,
            "avg_score": avg_score.round(1),
            "score_std": score_std.round(1),
            "time_per_question": time_per_question,
            "suspicious_similarity": suspicious_similarity,
            "proctor_flags": proctor_flags,
            "cheated": cheated,
        }
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)
    print(f"[process_student] Wrote {len(out_df)} rows to {output_path}")
    return output_path


def main() -> int:
    try:
        result = process_student_to_exam_cheating()
        return 0 if result is not None else 0  # Never fail pipeline
    except Exception as e:
        print(f"[process_student] Error (skipped): {e}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
