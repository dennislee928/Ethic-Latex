#!/bin/bash
# Ethical Riemann Hypothesis - Dependency Installation Script
# This script installs all required and optional dependencies

set -e  # Exit on error

echo "======================================================================"
echo "ETHICAL RIEMANN HYPOTHESIS - DEPENDENCY INSTALLATION"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.10+ first."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Found Python: $PYTHON_VERSION"

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip not found. Please install pip first."
    exit 1
fi

PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo ""
echo "======================================================================"
echo "STEP 1: Upgrade pip"
echo "======================================================================"
$PIP_CMD install --upgrade pip setuptools wheel

echo ""
echo "======================================================================"
echo "STEP 2: Core Dependencies (Required)"
echo "======================================================================"
echo "Installing: numpy, scipy, pandas"
$PIP_CMD install numpy scipy pandas

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install core dependencies"
    echo "Try: $PIP_CMD install --upgrade numpy scipy pandas"
    exit 1
fi
echo "✓ Core dependencies installed"

echo ""
echo "======================================================================"
echo "STEP 3: Visualization Dependencies (Required for figures)"
echo "======================================================================"
echo "Installing: matplotlib, seaborn, plotly"
$PIP_CMD install matplotlib seaborn plotly

if [ $? -ne 0 ]; then
    echo "WARNING: Failed to install visualization dependencies"
    echo "Figures will not be generated, but core functionality will work"
    echo "Try: $PIP_CMD install --upgrade matplotlib seaborn plotly"
else
    echo "✓ Visualization dependencies installed"
fi

echo ""
echo "======================================================================"
echo "STEP 4: Jupyter Notebook Dependencies (Optional)"
echo "======================================================================"
read -p "Install Jupyter notebooks? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $PIP_CMD install jupyter ipywidgets
    if [ $? -eq 0 ]; then
        echo "✓ Jupyter installed"
    else
        echo "WARNING: Failed to install Jupyter"
        echo "Try: $PIP_CMD install --upgrade jupyter ipywidgets"
    fi
else
    echo "Skipping Jupyter installation"
fi

echo ""
echo "======================================================================"
echo "STEP 5: Development Tools (Optional)"
echo "======================================================================"
read -p "Install development tools (black, pytest)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $PIP_CMD install black pytest
    if [ $? -eq 0 ]; then
        echo "✓ Development tools installed"
    else
        echo "WARNING: Failed to install development tools"
    fi
else
    echo "Skipping development tools"
fi

echo ""
echo "======================================================================"
echo "Verification"
echo "======================================================================"
echo "Testing imports..."

$PYTHON_CMD -c "import numpy; print('✓ numpy', numpy.__version__)" 2>/dev/null || echo "✗ numpy failed"
$PYTHON_CMD -c "import scipy; print('✓ scipy', scipy.__version__)" 2>/dev/null || echo "✗ scipy failed"
$PYTHON_CMD -c "import pandas; print('✓ pandas', pandas.__version__)" 2>/dev/null || echo "✗ pandas failed"
$PYTHON_CMD -c "import matplotlib; print('✓ matplotlib', matplotlib.__version__)" 2>/dev/null || echo "✗ matplotlib failed"
$PYTHON_CMD -c "import seaborn; print('✓ seaborn')" 2>/dev/null || echo "✗ seaborn failed"
$PYTHON_CMD -c "import plotly; print('✓ plotly', plotly.__version__)" 2>/dev/null || echo "✗ plotly failed"
$PYTHON_CMD -c "import jupyter; print('✓ jupyter')" 2>/dev/null || echo "✗ jupyter not installed (optional)"

echo ""
echo "======================================================================"
echo "Installation Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Run: bash quick-start-script/quick-start.sh"
echo "  2. Or: cd simulation && python run_example.py"
echo ""
