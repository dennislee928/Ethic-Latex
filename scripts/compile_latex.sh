#!/bin/bash
# Compile LaTeX Paper Script
# This script compiles the Ethical Riemann Hypothesis paper.
# Prefers latexmk when available for reliable builds including bibliography.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

TEX_MAIN="${1:-ethical_riemann_hypothesis.tex}"

echo "======================================================================"
echo "COMPILING LATEX PAPER: $TEX_MAIN"
echo "======================================================================"
echo ""

if ! command -v pdflatex &> /dev/null; then
    echo "ERROR: pdflatex not found!"
    echo ""
    echo "Please install a LaTeX distribution:"
    echo "  - Windows: MiKTeX (https://miktex.org/)"
    echo "  - macOS: MacTeX (https://www.tug.org/mactex/)"
    echo "  - Linux: sudo apt-get install texlive-full"
    exit 1
fi

echo "Found pdflatex: $(which pdflatex)"
echo ""

# Prefer latexmk when available (handles bibliography and multi-pass automatically)
if command -v latexmk &> /dev/null; then
    echo "Using latexmk for reliable build (bibliography handled automatically)..."
    latexmk -pdf -interaction=nonstopmode -file-line-error -halt-on-error "$TEX_MAIN"
    BUILD_OK=$?
else
    echo "latexmk not found, falling back to manual pdflatex + bibtex passes..."
    echo "[1/4] First pdflatex pass..."
    pdflatex -interaction=nonstopmode "$TEX_MAIN" > /dev/null 2>&1
    echo "[2/4] BibTeX..."
    BASE="${TEX_MAIN%.tex}"
    if command -v bibtex &> /dev/null; then
        bibtex "$BASE" > /dev/null 2>&1 || true
    fi
    echo "[3/4] Second pdflatex pass..."
    pdflatex -interaction=nonstopmode "$TEX_MAIN" > /dev/null 2>&1
    echo "[4/4] Third pdflatex pass..."
    pdflatex -interaction=nonstopmode "$TEX_MAIN" > /dev/null 2>&1
    BUILD_OK=0
fi

echo ""
PDF_NAME="${TEX_MAIN%.tex}.pdf"
if [ -f "$PDF_NAME" ] && [ "${BUILD_OK:-0}" -eq 0 ]; then
    echo "======================================================================"
    echo "SUCCESS! Paper compiled: $PDF_NAME"
    echo "======================================================================"
    ls -lh "$PDF_NAME"
else
    echo "======================================================================"
    echo "ERROR: PDF not generated. Check ${TEX_MAIN%.tex}.log for errors."
    echo "======================================================================"
    exit 1
fi

