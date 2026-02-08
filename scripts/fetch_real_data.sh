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

echo "Done. Run: python scripts/convert_adult_to_csv.py (to create data/adult.csv)"
