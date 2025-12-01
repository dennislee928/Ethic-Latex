#!/bin/bash
# Run unit tests for psychohistory integration modules

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "RUNNING UNIT TESTS FOR PSYCHOHISTORY INTEGRATION"
echo "======================================================================"
echo ""

# Check if pytest is available
if ! command -v pytest >/dev/null 2>&1 && ! python -m pytest --version >/dev/null 2>&1; then
    echo "ERROR: pytest not found. Install with: pip install pytest"
    exit 1
fi

# Determine pytest command
if command -v pytest >/dev/null 2>&1; then
    PYTEST_CMD="pytest"
else
    PYTEST_CMD="python -m pytest"
fi

echo "Using pytest command: $PYTEST_CMD"
echo ""

# Run tests
echo "Running unit tests..."
$PYTEST_CMD \
    test_temporal_erh.py \
    test_agent_framework.py \
    test_social_network.py \
    test_meta_monitor.py \
    test_hybrid_model.py \
    test_psychohistory_integration.py \
    -v \
    --tb=short

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "======================================================================"
    echo "SUCCESS: All unit tests passed!"
    echo "======================================================================"
else
    echo "======================================================================"
    echo "FAILURE: Some tests failed. Check output above for details."
    echo "======================================================================"
fi

exit $EXIT_CODE


