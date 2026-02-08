#!/bin/bash
# Full ERH pipeline: simulation batch → phase transition → comprehensive report
# Usage: ./scripts/run_full_pipeline.sh [OUTPUT_DIR]
#   OUTPUT_DIR defaults to "results"

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT:$ROOT/erh_core:$PYTHONPATH"

OUTPUT_DIR="${1:-results}"
mkdir -p "$OUTPUT_DIR" simulation/output/figures final_report

echo "[1/3] Running simulation batch..."
python scripts/run_simulation_batch.py \
  --complexity-dist zipf \
  --output-dir "$OUTPUT_DIR" \
  --instances 2 \
  || true

echo "[2/3] Running phase transition experiment..."
python scripts/run_phase_transition_exp.py \
  --no-oracle \
  --save-plot \
  || true

echo "[3/3] Generating comprehensive report..."
python scripts/generate_comprehensive_report.py \
  --input-dir "$OUTPUT_DIR" \
  --output-dir final_report \
  || true

echo "Pipeline complete. LaTeX snippet: simulation/output/figures_latex_code.tex"
