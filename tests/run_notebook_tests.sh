#!/bin/bash
# Run Robot Framework tests for Jupyter notebooks

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "RUNNING NOTEBOOK TESTS WITH ROBOT FRAMEWORK"
echo "======================================================================"
echo ""

# Check if Robot Framework is installed
if ! command -v robot &> /dev/null; then
    echo "ERROR: Robot Framework not found!"
    echo ""
    echo "Install with:"
    echo "  pip install robotframework robotframework-jupyterlibrary"
    echo ""
    echo "Or install all dependencies:"
    echo "  pip install -r ../requirements.txt"
    exit 1
fi

echo "Found robot: $(which robot)"
echo ""

# Create output directory if it doesn't exist
mkdir -p notebooks/output

# Run tests
echo "Running notebook tests..."
robot \
    --outputdir notebooks/output \
    --log notebooks/output/log.html \
    --report notebooks/output/report.html \
    --xunit notebooks/output/xunit.xml \
    notebooks/notebook_tests.robot

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "======================================================================"
    echo "SUCCESS: All notebook tests passed!"
    echo "======================================================================"
    echo ""
    echo "Test results:"
    echo "  - Log: notebooks/output/log.html"
    echo "  - Report: notebooks/output/report.html"
else
    echo "======================================================================"
    echo "FAILURE: Some tests failed. Check notebooks/output/log.html for details."
    echo "======================================================================"
fi

exit $EXIT_CODE

