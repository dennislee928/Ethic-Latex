#!/bin/bash
# Compile LaTeX Paper Script
# This script compiles the Ethical Riemann Hypothesis paper

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "COMPILING LATEX PAPER"
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

# Clean previous builds (optional)
# rm -f *.aux *.log *.out *.toc *.bbl *.blg *.synctex.gz

echo "[1/4] First pdflatex pass..."
pdflatex -interaction=nonstopmode ethical_riemann_hypothesis.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Completed"
else
    echo "  ⚠ Completed with warnings (check ethical_riemann_hypothesis.log)"
fi

if command -v bibtex &> /dev/null; then
    echo "[2/4] Running BibTeX..."
    bibtex ethical_riemann_hypothesis > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ Completed"
    else
        echo "  ⚠ Completed with warnings"
    fi
else
    echo "[2/4] BibTeX not found, skipping bibliography"
fi

echo "[3/4] Second pdflatex pass..."
pdflatex -interaction=nonstopmode ethical_riemann_hypothesis.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Completed"
else
    echo "  ⚠ Completed with warnings"
fi

echo "[4/4] Third pdflatex pass..."
pdflatex -interaction=nonstopmode ethical_riemann_hypothesis.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Completed"
else
    echo "  ⚠ Completed with warnings"
fi

echo ""
if [ -f "ethical_riemann_hypothesis.pdf" ]; then
    echo "======================================================================"
    echo "SUCCESS! Paper compiled: ethical_riemann_hypothesis.pdf"
    echo "======================================================================"
    ls -lh ethical_riemann_hypothesis.pdf
else
    echo "======================================================================"
    echo "ERROR: PDF not generated. Check ethical_riemann_hypothesis.log for errors."
    echo "======================================================================"
    exit 1
fi

