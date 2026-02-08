#!/usr/bin/env bash
# Local verification of build_thesis_gated.yml thesis job
# Simulates build_thesis.yml steps for macOS ( BasicTeX path, pdflatex/xelatex )
# Usage: source .venv/bin/activate && ./scripts/verify_thesis_build_local.sh
#   Or: ./scripts/verify_thesis_build_local.sh  (will try to use .venv)

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT:$ROOT/erh_core:$ROOT/simulation:$PYTHONPATH"

# Use project .venv if not already in a venv
if [ -z "${VIRTUAL_ENV:-}" ] && [ -f "$ROOT/.venv/bin/activate" ]; then
  echo "Activating .venv..."
  source "$ROOT/.venv/bin/activate"
fi

# TeX path for BasicTeX 2025 on macOS
TEXBIN="/usr/local/texlive/2025basic/bin/universal-darwin"
if [ -d "$TEXBIN" ]; then
  export PATH="$TEXBIN:$PATH"
else
  echo "Warning: $TEXBIN not found. Ensure TeX is in PATH."
fi

echo "=== [1/12] LLM stress test (dry-run) ==="
python scripts/llm_stress_test.py --num-actions 20 --dry-run --output-dir llm_stress_test_results || true

echo "=== [2/12] Generate figures ==="
mkdir -p simulation/output/figures simulation/output
python -m simulation.generate_all_figures || true

echo "=== [3/12] Quantum phase transition ==="
python scripts/run_quantum_phase_transition.py --save-plot --n-points 10 || true

echo "=== [4/12] Phase transition experiment ==="
python scripts/run_phase_transition_exp.py --no-oracle --save-plot --output-dir simulation/output || true

echo "=== [5/12] Real-data case studies ==="
python -m simulation.real_data.adult_income_case_study || true
python -m simulation.real_data.exam_cheating_case_study || true
python -m simulation.real_data.sexual_abuse_case_study || true

echo "=== [6/12] Prepare figures for LaTeX ==="
mkdir -p figures
cp simulation/output/figures/*.pdf figures/ 2>/dev/null || true
cp simulation/output/figures/latest_quantum_circuit.png figures/ 2>/dev/null || true
cp simulation/output/figures/latest_quantum_distribution.png figures/ 2>/dev/null || true
cp llm_stress_test_results/llm_stress_test_Pi_E.png figures/ 2>/dev/null || true

echo "=== [7/12] Integrate figures ==="
python scripts/integrate_figures.py || true

echo "=== [8/12] Update LaTeX content ==="
python scripts/update_latex.py || true

echo "=== [9/12] Generate MD reports ==="
python scripts/generate_md_reports.py || true

echo "=== [10/12] Compile English LaTeX (pdflatex) ==="
if command -v pdflatex &>/dev/null; then
  pdflatex -interaction=nonstopmode -file-line-error -halt-on-error ethical_riemann_hypothesis_en.tex
  bibtex ethical_riemann_hypothesis_en || true
  pdflatex -interaction=nonstopmode -file-line-error -halt-on-error ethical_riemann_hypothesis_en.tex
  pdflatex -interaction=nonstopmode -file-line-error -halt-on-error ethical_riemann_hypothesis_en.tex
  echo "✓ ethical_riemann_hypothesis_en.pdf"
else
  echo "⚠ pdflatex not found, skipping English PDF"
fi

echo "=== [11/12] Compile Chinese LaTeX (xelatex) ==="
if command -v xelatex &>/dev/null; then
  xelatex -interaction=nonstopmode -file-line-error -halt-on-error ethical_riemann_hypothesis_zh.tex 2>/dev/null || true
  if [ -f ethical_riemann_hypothesis_zh.aux ]; then
    bibtex ethical_riemann_hypothesis_zh 2>/dev/null || true
    xelatex -interaction=nonstopmode -file-line-error -halt-on-error ethical_riemann_hypothesis_zh.tex 2>/dev/null || true
    xelatex -interaction=nonstopmode -file-line-error -halt-on-error ethical_riemann_hypothesis_zh.tex 2>/dev/null || true
  fi
  [ -f ethical_riemann_hypothesis_zh.pdf ] && echo "✓ ethical_riemann_hypothesis_zh.pdf" || echo "⚠ Chinese PDF skipped (install: tlmgr install xecjk ctex; or fonts-noto-cjk)"
else
  echo "⚠ xelatex not found, skipping Chinese PDF"
fi

echo "=== [12/12] Summary ==="
[ -f ethical_riemann_hypothesis_en.pdf ] && echo "✓ ethical_riemann_hypothesis_en.pdf ($(wc -c < ethical_riemann_hypothesis_en.pdf) bytes)"
[ -f ethical_riemann_hypothesis_zh.pdf ] && echo "✓ ethical_riemann_hypothesis_zh.pdf ($(wc -c < ethical_riemann_hypothesis_zh.pdf) bytes)"
echo "Done."
