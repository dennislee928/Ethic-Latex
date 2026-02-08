#!/bin/bash
# Full ERH pipeline: simulation batch → phase transition → comprehensive report
# Usage: ./scripts/run_full_pipeline.sh [OUTPUT_DIR]
#   OUTPUT_DIR defaults to "results"
#   Set FULL=1 to also run generate_all_figures (comparison table, paper figures)
#   Example: FULL=1 ./scripts/run_full_pipeline.sh results

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT:$ROOT/erh_core:$PYTHONPATH"

OUTPUT_DIR="${1:-results}"
mkdir -p "$OUTPUT_DIR" simulation/output/figures final_report

echo "[1/4] Running simulation batch..."
python scripts/run_simulation_batch.py \
  --complexity-dist zipf \
  --output-dir "$OUTPUT_DIR" \
  --instances 2 \
  || true

echo "[2/4] Running phase transition experiment..."
python scripts/run_phase_transition_exp.py \
  --no-oracle \
  --save-plot \
  --output-dir simulation/output \
  || true

if [ "${FULL:-0}" = "1" ]; then
  echo "[3/4] Generating all figures (comparison table, paper figures)..."
  python -m simulation.generate_all_figures || true
else
  echo "[3/4] Skipping generate_all_figures (set FULL=1 to include)"
fi

echo "[4/4] Generating comprehensive report..."
python scripts/generate_comprehensive_report.py \
  --input-dir "$OUTPUT_DIR" \
  --output-dir final_report \
  || true

echo "Pipeline complete."
echo "  - LaTeX snippet: simulation/output/figures_latex_code.tex"
echo "  - Phase transition: simulation/output/figures/phase_transition.png"
echo "  - For full figures (comparison table, paper PDFs): FULL=1 ./scripts/run_full_pipeline.sh"
