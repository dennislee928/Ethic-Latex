#!/bin/bash
# Fetch real-world datasets for ERH case studies
# Usage: ./scripts/fetch_real_data.sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/data" "$ROOT/data/real_world"

echo "Fetching Adult Income (UCI)..."
wget -q "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data" \
  -O "$ROOT/data/real_world/adult.data" 2>/dev/null || true
wget -q "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.test" \
  -O "$ROOT/data/real_world/adult.test" 2>/dev/null || true

echo "Fetching COMPAS (ProPublica)..."
curl -sL "https://raw.githubusercontent.com/propublica/compas-analysis/master/compas-scores-two-years.csv" \
  -o "$ROOT/data/compas-scores-two-years.csv" 2>/dev/null || true

echo "Done. Run: python scripts/convert_adult_to_csv.py (to create data/adult.csv)"
