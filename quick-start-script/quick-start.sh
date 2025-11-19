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
if command -v jupyter &> /dev/null; then
    echo "Jupyter found. Opening notebooks..."
    cd simulation/notebooks
    echo "Starting Jupyter notebook server..."
    echo "The notebook will open in your browser."
    echo "Press Ctrl+C to stop the server."
    jupyter notebook
    cd "$PROJECT_ROOT"
else
    echo "Jupyter not found."
    echo "To open Jupyter notebooks, run:"
    echo "  cd simulation/notebooks"
    echo "  jupyter notebook"
    echo ""
    echo "Or install Jupyter first: pip install jupyter"
fi

echo ""
echo "======================================================================"
echo "STEP 4: Compile LaTeX Paper (optional - requires LaTeX)"
echo "======================================================================"
if command -v pdflatex &> /dev/null; then
    echo "LaTeX found. Compiling paper..."
    echo "This may take a few minutes..."
    
    # First pass
    if pdflatex -interaction=nonstopmode ethical_riemann_hypothesis.tex > /dev/null 2>&1; then
        echo "  [1/4] First pdflatex pass completed"
    else
        echo "  [1/4] First pdflatex pass completed (with warnings)"
    fi
    
    # BibTeX
    if command -v bibtex &> /dev/null; then
        if bibtex ethical_riemann_hypothesis > /dev/null 2>&1; then
            echo "  [2/4] BibTeX completed"
        else
            echo "  [2/4] BibTeX completed (with warnings)"
        fi
    else
        echo "  [2/4] BibTeX not found, skipping bibliography"
    fi
    
    # Second pass
    if pdflatex -interaction=nonstopmode ethical_riemann_hypothesis.tex > /dev/null 2>&1; then
        echo "  [3/4] Second pdflatex pass completed"
    else
        echo "  [3/4] Second pdflatex pass completed (with warnings)"
    fi
    
    # Third pass
    if pdflatex -interaction=nonstopmode ethical_riemann_hypothesis.tex > /dev/null 2>&1; then
        echo "  [4/4] Third pdflatex pass completed"
    else
        echo "  [4/4] Third pdflatex pass completed (with warnings)"
    fi
    
    if [ -f "ethical_riemann_hypothesis.pdf" ]; then
        echo "Paper compiled successfully: ethical_riemann_hypothesis.pdf"
    else
        echo "WARNING: PDF file not generated. Check LaTeX errors above."
    fi
else
    echo "WARNING: pdflatex not found. Skipping LaTeX compilation."
    echo "Install a LaTeX distribution:"
    echo "  - Windows: MiKTeX (https://miktex.org/)"
    echo "  - macOS: MacTeX (https://www.tug.org/mactex/)"
    echo "  - Linux: sudo apt-get install texlive-full"
fi

echo ""
echo "======================================================================"
echo "Quick start complete!"
echo "======================================================================"