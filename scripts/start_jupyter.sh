#!/bin/bash
# Start Jupyter Notebook Server

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/../simulation/notebooks"

echo "======================================================================"
echo "STARTING JUPYTER NOTEBOOK SERVER"
echo "======================================================================"
echo ""
echo "Notebook directory: $(pwd)"
echo ""
echo "The Jupyter interface will open in your browser."
echo "Press Ctrl+C to stop the server."
echo ""
echo "======================================================================"
echo ""

# Try multiple ways to start Jupyter
if command -v jupyter &> /dev/null; then
    echo "Using: jupyter notebook"
    jupyter notebook
elif python -c "import notebook" 2>/dev/null; then
    echo "Using: python -m notebook"
    python -m notebook
elif python3 -c "import notebook" 2>/dev/null; then
    echo "Using: python3 -m notebook"
    python3 -m notebook
elif python -c "import jupyterlab" 2>/dev/null; then
    echo "Using: python -m jupyterlab (JupyterLab instead of Notebook)"
    python -m jupyterlab
else
    echo "ERROR: Jupyter not found!"
    echo ""
    echo "Install Jupyter with:"
    echo "  pip install jupyter ipywidgets"
    echo ""
    echo "Or use:"
    echo "  bash scripts/install_dependencies.sh"
    echo ""
    echo "If Jupyter is installed but command not found, try:"
    echo "  python -m notebook"
    exit 1
fi
