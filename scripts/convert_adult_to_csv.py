#!/usr/bin/env python3
"""
Convert UCI Adult Income data format to CSV with header for adult_income_case_study.

UCI adult.data / adult.test: comma-separated, no header. Columns (per adult.names):
  age, workclass, fnlwgt, education, education-num, marital-status, occupation,
  relationship, race, sex, capital-gain, capital-loss, hours-per-week,
  native-country, income

Output: data/adult.csv with income column. Rows with '?' are dropped.
"""

from pathlib import Path

COLS = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education-num",
    "marital-status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital-gain",
    "capital-loss",
    "hours-per-week",
    "native-country",
    "income",
]


def _read_lines(path: Path) -> list[str]:
    """Read lines, skip empty and malformed."""
    lines = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "|" in line and "Cross validator" in line:
                continue
            lines.append(line)
    return lines


def convert_adult_to_csv(
    data_path: Path | None = None,
    test_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    """
    Convert UCI adult.data and adult.test to CSV.

    Parameters
    ----------
    data_path : Path, optional
        Path to adult.data. Default: data/real_world/adult.data
    test_path : Path, optional
        Path to adult.test. Default: data/real_world/adult.test
    output_path : Path, optional
        Output CSV. Default: data/adult.csv

    Returns
    -------
    Path
        Path to written CSV.
    """
    root = Path(__file__).resolve().parents[1]
    data_path = data_path or root / "data" / "real_world" / "adult.data"
    test_path = test_path or root / "data" / "real_world" / "adult.test"
    output_path = output_path or root / "data" / "adult.csv"

    if not data_path.exists():
        print(f"[convert_adult] No {data_path}; run scripts/fetch_real_data.sh first.")
        return output_path

    rows = []
    for p in [data_path, test_path]:
        if not p.exists():
            continue
        for line in _read_lines(p):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 15:
                continue
            if "?" in parts:
                continue
            if parts[-1] not in (">50K", "<=50K", ">50K.", "<=50K."):
                continue
            income = ">50K" if ">50K" in parts[-1] else "<=50K"
            parts[-1] = income
            rows.append(parts)

    if not rows:
        print("[convert_adult] No valid rows found.")
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(",".join(COLS) + "\n")
        for r in rows:
            f.write(",".join(r) + "\n")

    print(f"[convert_adult] Wrote {len(rows)} rows to {output_path}")
    return output_path


if __name__ == "__main__":
    convert_adult_to_csv()
