#!/bin/bash
# Start Jupyter Notebook Server

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/simulation/notebooks"

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

if command -v jupyter &> /dev/null; then
    jupyter notebook
else
    echo "ERROR: Jupyter not found!"
    echo ""
    echo "Install Jupyter with:"
    echo "  pip install jupyter ipywidgets"
    echo ""
    echo "Or use:"
    echo "  bash install_dependencies.sh"
    exit 1
fi

