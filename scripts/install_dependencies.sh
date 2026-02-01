#!/bin/bash
# Ethical Riemann Hypothesis - Dependency Installation Script
# Uses virtual environment to avoid PEP 668 externally-managed-environment
# (Homebrew Python on macOS blocks pip install to system Python)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="${VENV_DIR:-$PROJECT_ROOT/.venv}"

echo "======================================================================"
echo "ETHICAL RIEMANN HYPOTHESIS - DEPENDENCY INSTALLATION"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.10+ first."
    exit 1
fi

PYTHON_CMD="python3"
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Found Python: $PYTHON_VERSION"

echo ""
echo "======================================================================"
echo "STEP 1: Create/use virtual environment"
echo "======================================================================"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv at $VENV_DIR"
    $PYTHON_CMD -m venv "$VENV_DIR"
else
    echo "Using existing venv at $VENV_DIR"
fi
echo "Activate with: source $VENV_DIR/bin/activate"

PIP_CMD="$VENV_DIR/bin/pip"
PYTHON_VENV="$VENV_DIR/bin/python"

echo ""
echo "======================================================================"
echo "STEP 2: Upgrade pip & install editable package"
echo "======================================================================"
$PIP_CMD install --upgrade pip setuptools wheel
$PIP_CMD install -e .

echo ""
echo "======================================================================"
echo "STEP 3: Core Dependencies (Required)"
echo "======================================================================"
$PIP_CMD install numpy scipy pandas scikit-learn networkx

echo ""
echo "======================================================================"
echo "STEP 4: Visualization Dependencies"
echo "======================================================================"
$PIP_CMD install matplotlib seaborn plotly

echo ""
echo "======================================================================"
echo "STEP 5: Development Tools"
echo "======================================================================"
$PIP_CMD install black pytest pydantic

echo ""
echo "======================================================================"
echo "STEP 6: Optional - Quantum (Phase 3)"
echo "======================================================================"
echo "Quantum module works WITHOUT qiskit-aer (uses NumPy fallback)."
echo "Install qiskit-aer only if you want native simulation (may fail on Python 3.14 or AppleClang 17)."
read -p "Install qiskit qiskit-aer? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $PIP_CMD install qiskit qiskit-aer 2>/dev/null || echo "qiskit-aer build failed; quantum module will use NumPy fallback."
fi

echo ""
echo "======================================================================"
echo "Verification"
echo "======================================================================"
$PYTHON_VENV -c "import numpy; print('✓ numpy', numpy.__version__)"
$PYTHON_VENV -c "import simulation; print('✓ simulation')"
$PYTHON_VENV -m pytest --version 2>/dev/null || echo "Note: run 'source .venv/bin/activate' then 'pytest tests/'"

echo ""
echo "======================================================================"
echo "Installation Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Activate venv:  source $VENV_DIR/bin/activate"
echo "  2. Run scripts:    python scripts/calculate_alpha_comparison.py"
echo "  3. Run tests:      pytest tests/test_psychohistory_integration.py -v"
echo ""
