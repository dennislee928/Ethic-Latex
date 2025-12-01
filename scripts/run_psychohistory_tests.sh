#!/bin/bash
# Run psychohistory simulation tests
# Usage: bash scripts/run_psychohistory_tests.sh [--quick]

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Psychohistory Simulation Tests"
echo "=========================================="
echo ""

# Check for quick mode
QUICK_MODE=false
if [ "$1" == "--quick" ]; then
    QUICK_MODE=true
    echo "Running in QUICK mode (parameter sweep only)"
else
    echo "Running in FULL mode (all tests)"
fi
echo ""

# Step 1: Install dependencies
echo "[1/4] Checking dependencies..."
python -m pip install --upgrade pip --quiet
if [ -f requirements.txt ]; then
    pip install -r requirements.txt --quiet
fi
echo "✓ Dependencies checked"
echo ""

# Step 2: Set up environment
echo "[2/4] Setting up environment..."
export PYTHONPATH="$PYTHONPATH:$PROJECT_ROOT"
export PYTHONPATH="$PYTHONPATH:$PROJECT_ROOT/simulation"
echo "✓ Environment set up"
echo ""

# Step 3: Create output directory
echo "[3/4] Creating output directory..."
mkdir -p simulation/output/psychohistory_tests
echo "✓ Output directory ready"
echo ""

# Step 4: Run simulation tests
echo "[4/4] Running psychohistory simulation tests..."
if [ "$QUICK_MODE" = true ]; then
    python scripts/run_psychohistory_simulations.py --quick --output-dir simulation/output/psychohistory_tests
else
    python scripts/run_psychohistory_simulations.py --output-dir simulation/output/psychohistory_tests
fi

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "=========================================="
    echo "SUCCESS: All tests completed!"
    echo "=========================================="
    echo ""
    echo "Test results:"
    echo "  - JSON Report: simulation/output/psychohistory_tests/test_report.json"
    echo "  - Text Summary: simulation/output/psychohistory_tests/test_summary.txt"
else
    echo "=========================================="
echo "FAILURE: Some tests failed"
echo "=========================================="
fi
exit $EXIT_CODE
