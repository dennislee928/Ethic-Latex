#!/bin/bash
# Run Robot Framework tests for Jupyter notebooks

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "RUNNING NOTEBOOK TESTS WITH ROBOT FRAMEWORK"
echo "======================================================================"
echo ""

# Check if Robot Framework is installed
# Try multiple ways to find robot command
ROBOT_CMD=""

# Check if robot command exists in PATH
if command -v robot >/dev/null 2>&1; then
    ROBOT_CMD="robot"
    echo "Found robot command in PATH"
elif python -m robot --version >/dev/null 2>&1 || python -m robot --version 2>&1 | grep -q "Robot Framework"; then
    ROBOT_CMD="python -m robot"
    echo "Found robot via: python -m robot"
elif python3 -m robot --version >/dev/null 2>&1 || python3 -m robot --version 2>&1 | grep -q "Robot Framework"; then
    ROBOT_CMD="python3 -m robot"
    echo "Found robot via: python3 -m robot"
else
    # Last resort: try python -m robot anyway (it might work even if version check fails)
    echo "WARNING: Could not verify Robot Framework installation"
    echo "Attempting to use: python -m robot"
    ROBOT_CMD="python -m robot"
fi

echo "Using robot command: $ROBOT_CMD"
echo ""

# Create output directory if it doesn't exist
mkdir -p notebooks/output

# Run tests
echo "Running notebook tests..."
$ROBOT_CMD \
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

