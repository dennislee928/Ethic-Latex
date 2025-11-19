#!/bin/bash
# Ethical Riemann Hypothesis - Quick Start Script
# This script should be run from the project root directory

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root (parent of script directory)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Project root: $PROJECT_ROOT"
echo "Changing to project root..."
cd "$PROJECT_ROOT"

# Check if we're in the right directory
if [ ! -d "simulation" ]; then
    echo "ERROR: 'simulation' directory not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

echo ""
echo "======================================================================"
echo "STEP 1: Quick Example"
echo "======================================================================"
cd simulation
python run_example.py

echo ""
echo "======================================================================"
echo "STEP 2: Generate All Figures (optional - requires matplotlib)"
echo "======================================================================"
echo "Checking if matplotlib is installed..."
if python -c "import matplotlib" 2>/dev/null; then
    echo "matplotlib found. Generating figures..."
    python generate_all_figures.py
else
    echo "WARNING: matplotlib not installed. Skipping figure generation."
    echo "Install with: pip install matplotlib seaborn"
fi

cd "$PROJECT_ROOT"

echo ""
echo "======================================================================"
echo "STEP 3: Jupyter Notebooks (optional)"
echo "======================================================================"
echo "To open Jupyter notebooks, run:"
echo "  cd simulation/notebooks"
echo "  jupyter notebook"
echo ""
echo "Or install Jupyter first: pip install jupyter"

echo ""
echo "======================================================================"
echo "STEP 4: Compile LaTeX Paper (optional - requires LaTeX)"
echo "======================================================================"
if command -v pdflatex &> /dev/null; then
    echo "LaTeX found. Compiling paper..."
    pdflatex ethical_riemann_hypothesis.tex
    bibtex ethical_riemann_hypothesis
    pdflatex ethical_riemann_hypothesis.tex
    pdflatex ethical_riemann_hypothesis.tex
    echo "Paper compiled successfully!"
else
    echo "WARNING: pdflatex not found. Skipping LaTeX compilation."
    echo "Install a LaTeX distribution (e.g., MiKTeX, TeX Live)"
fi

echo ""
echo "======================================================================"
echo "Quick start complete!"
echo "======================================================================"