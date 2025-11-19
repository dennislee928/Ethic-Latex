#!/bin/bash
# Ethical Riemann Hypothesis - Dependency Installation Script
# This script installs all required and optional dependencies

echo "======================================================================"
echo "ETHICAL RIEMANN HYPOTHESIS - DEPENDENCY INSTALLATION"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python: $python_version"

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "ERROR: pip not found. Please install pip first."
    exit 1
fi

echo ""
echo "======================================================================"
echo "STEP 1: Core Dependencies (Required)"
echo "======================================================================"
echo "Installing: numpy, scipy, pandas"
pip install --upgrade pip
pip install numpy scipy pandas

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install core dependencies"
    exit 1
fi
echo "✓ Core dependencies installed"

echo ""
echo "======================================================================"
echo "STEP 2: Visualization Dependencies (Required for figures)"
echo "======================================================================"
echo "Installing: matplotlib, seaborn, plotly"
pip install matplotlib seaborn plotly

if [ $? -ne 0 ]; then
    echo "WARNING: Failed to install visualization dependencies"
    echo "Figures will not be generated, but core functionality will work"
else
    echo "✓ Visualization dependencies installed"
fi

echo ""
echo "======================================================================"
echo "STEP 3: Jupyter Notebook Dependencies (Optional)"
echo "======================================================================"
read -p "Install Jupyter notebooks? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install jupyter ipywidgets
    if [ $? -eq 0 ]; then
        echo "✓ Jupyter installed"
    else
        echo "WARNING: Failed to install Jupyter"
    fi
else
    echo "Skipping Jupyter installation"
fi

echo ""
echo "======================================================================"
echo "STEP 4: Development Tools (Optional)"
echo "======================================================================"
read -p "Install development tools (black, pytest)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install black pytest
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

python -c "import numpy; print('✓ numpy', numpy.__version__)" 2>/dev/null || echo "✗ numpy failed"
python -c "import scipy; print('✓ scipy', scipy.__version__)" 2>/dev/null || echo "✗ scipy failed"
python -c "import pandas; print('✓ pandas', pandas.__version__)" 2>/dev/null || echo "✗ pandas failed"
python -c "import matplotlib; print('✓ matplotlib', matplotlib.__version__)" 2>/dev/null || echo "✗ matplotlib failed"
python -c "import seaborn; print('✓ seaborn')" 2>/dev/null || echo "✗ seaborn failed"
python -c "import plotly; print('✓ plotly', plotly.__version__)" 2>/dev/null || echo "✗ plotly failed"
python -c "import jupyter; print('✓ jupyter')" 2>/dev/null || echo "✗ jupyter not installed (optional)"

echo ""
echo "======================================================================"
echo "Installation Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Run: bash quick-start-script/quick-start.sh"
echo "  2. Or: cd simulation && python run_example.py"
echo ""

