#!/bin/bash
# Build Thesis Script
# This script performs all steps needed to generate the bilingual thesis PDFs
# Usage: bash scripts/build_thesis.sh

set -e  # Exit on error

echo "=========================================="
echo "Ethical Riemann Hypothesis - Thesis Build"
echo "=========================================="
echo ""

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"
echo ""

# Step 1: Install Python dependencies
echo "[1/9] Installing Python dependencies..."
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi
pip install papermill ipykernel nbconvert
echo "✓ Dependencies installed"
echo ""

# Step 2: Set up environment
echo "[2/9] Setting up environment..."
export PYTHONPATH="$PYTHONPATH:$PROJECT_ROOT"
echo "✓ PYTHONPATH set to: $PYTHONPATH"
echo ""

# Step 3: Create necessary output directories
echo "[3/9] Creating output directories..."
mkdir -p simulation/output/figures
mkdir -p figures
mkdir -p simulation/notebooks
echo "✓ Directories created"
echo ""

# Step 4: Run simulation and generate figures
echo "[4/9] Running simulation and generating figures..."
cd "$PROJECT_ROOT/simulation"
# Ensure output directory exists before running
mkdir -p output/figures
mkdir -p output
python generate_all_figures.py
cd "$PROJECT_ROOT"
echo "✓ Figures generated"
echo ""

# Step 5: Install Jupyter kernel
echo "[5/9] Installing Jupyter kernel..."
python -m ipykernel install --user --name python3
echo "✓ Kernel installed"
echo ""

# Step 6: Execute notebooks (with error handling)
echo "[6/9] Executing notebooks..."
cd "$PROJECT_ROOT"

# Ensure output directories exist before running notebooks
mkdir -p simulation/output/figures
mkdir -p simulation/output

# List of notebooks to execute
NOTEBOOKS=(
    "01_basic_simulation.ipynb"
    "02_judge_comparison.ipynb"
    "03_zeta_zeros.ipynb"
    "04_parameter_sensitivity.ipynb"
    "06_baseline_comparison.ipynb"
    "07_zeta_zeros_deep_analysis.ipynb"
)

# Change to notebooks directory so relative paths work correctly
cd "$PROJECT_ROOT/simulation/notebooks"

# Execute each notebook from the notebooks directory
for notebook in "${NOTEBOOKS[@]}"; do
    if [ -f "$notebook" ]; then
        echo "  Executing: $notebook"
        output_notebook="${notebook%.ipynb}_out.ipynb"
        # Use -k to explicitly specify kernel, and execute from notebooks directory
        papermill -k python3 "$notebook" "$output_notebook" || {
            echo "  ⚠ Warning: Notebook $notebook failed, continuing..."
        }
    else
        echo "  ⚠ Warning: Notebook $notebook not found, skipping..."
    fi
done

# Return to project root
cd "$PROJECT_ROOT"
echo "✓ Notebooks executed"
echo ""

# Step 7: Prepare figures for LaTeX
echo "[7/9] Preparing figures for LaTeX..."
mkdir -p figures
# Copy figures from simulation/output/figures (where generate_all_figures.py saves them)
if [ -d "simulation/output/figures" ] && [ "$(ls -A simulation/output/figures/*.pdf 2>/dev/null)" ]; then
    cp simulation/output/figures/*.pdf figures/ 2>/dev/null || true
    echo "  Copied figures from simulation/output/figures:"
    ls -1 figures/*.pdf 2>/dev/null | wc -l | xargs echo "    Total:"
elif [ -d "simulation/output/figures" ]; then
    echo "  ⚠ Warning: simulation/output/figures directory exists but is empty"
else
    echo "  ⚠ Warning: simulation/output/figures directory not found"
fi
echo "✓ Figures prepared"
echo ""

# Step 8: Integrate figures and update LaTeX content
echo "[8/9] Integrating figures and updating LaTeX content..."
python scripts/integrate_figures.py
python scripts/update_latex.py
echo "✓ LaTeX content updated"
echo ""

# Step 9: Compile LaTeX documents
echo "[9/9] Compiling LaTeX documents..."

# Check if xelatex is available
if command -v xelatex &> /dev/null; then
    echo "  Compiling English version..."
    cd "$PROJECT_ROOT"
    xelatex -interaction=nonstopmode ethical_riemann_hypothesis_en.tex > /dev/null 2>&1 || true
    xelatex -interaction=nonstopmode ethical_riemann_hypothesis_en.tex > /dev/null 2>&1 || true
    bibtex ethical_riemann_hypothesis_en || true
    xelatex -interaction=nonstopmode ethical_riemann_hypothesis_en.tex > /dev/null 2>&1 || true
    
    echo "  Compiling Chinese version..."
    xelatex -interaction=nonstopmode ethical_riemann_hypothesis_zh.tex > /dev/null 2>&1 || true
    xelatex -interaction=nonstopmode ethical_riemann_hypothesis_zh.tex > /dev/null 2>&1 || true
    bibtex ethical_riemann_hypothesis_zh || true
    xelatex -interaction=nonstopmode ethical_riemann_hypothesis_zh.tex > /dev/null 2>&1 || true
    
    echo "✓ LaTeX compilation completed"
else
    echo "  ⚠ Warning: xelatex not found, skipping compilation"
    echo "  (This is expected in CI environments - compilation will be done by latex-action)"
fi
echo ""

# Summary
echo "=========================================="
echo "Build Summary"
echo "=========================================="
echo ""

if [ -f "ethical_riemann_hypothesis_en.pdf" ]; then
    echo "✓ English PDF: ethical_riemann_hypothesis_en.pdf"
else
    echo "⚠ English PDF: Not found (will be generated by CI)"
fi

if [ -f "ethical_riemann_hypothesis_zh.pdf" ]; then
    echo "✓ Chinese PDF: ethical_riemann_hypothesis_zh.pdf"
else
    echo "⚠ Chinese PDF: Not found (will be generated by CI)"
fi

echo ""
echo "Figures generated: $(ls -1 figures/*.pdf 2>/dev/null | wc -l)"
echo ""
echo "=========================================="
echo "Build completed!"
echo "=========================================="

