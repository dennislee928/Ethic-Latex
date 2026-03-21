#!/bin/bash
# Fetch real-world datasets for ERH case studies
# Usage: ./scripts/fetch_real_data.sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/data" "$ROOT/data/real_world"

echo "Fetching Adult Income (UCI)..."
curl -sL "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data" \
  -o "$ROOT/data/real_world/adult.data" || true
curl -sL "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.test" \
  -o "$ROOT/data/real_world/adult.test" || true

echo "Fetching COMPAS (ProPublica)..."
curl -sL "https://raw.githubusercontent.com/propublica/compas-analysis/master/compas-scores-two-years.csv" \
  -o "$ROOT/data/compas-scores-two-years.csv" || true

echo "Fetching UCI Student Performance (exam cheating proxy)..."
curl -sL "https://archive.ics.uci.edu/static/public/320/student+performance.zip" \
  -o "$ROOT/data/real_world/student_perf.zip" || true
if [ -f "$ROOT/data/real_world/student_perf.zip" ]; then
  unzip -o "$ROOT/data/real_world/student_perf.zip" -d "$ROOT/data/real_world" || true
  # UCI zip contains nested student.zip; extract inner zip
  if [ -f "$ROOT/data/real_world/student.zip" ]; then
    unzip -o "$ROOT/data/real_world/student.zip" -d "$ROOT/data/real_world" || true
  fi
  # Move CSVs to real_world root (may be in subdir)
  find "$ROOT/data/real_world" \( -name "student-mat.csv" -o -name "student-por.csv" \) 2>/dev/null | while read -r f; do
    if [ -f "$f" ] && [ "$(dirname "$f")" != "$ROOT/data/real_world" ]; then
      mv "$f" "$ROOT/data/real_world/"
    fi
  done
fi

echo "Done. Run: python scripts/convert_adult_to_csv.py (adult.csv)"
echo "       python scripts/process_student_to_exam_cheating.py (exam_cheating_cases.csv)"
echo "       python scripts/generate_synthetic_sexual_abuse.py (sexual_abuse_cases.csv)"
