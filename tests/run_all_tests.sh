#!/bin/bash
# Run all tests: unit tests + notebook tests

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "RUNNING ALL TESTS"
echo "======================================================================"
echo ""

EXIT_CODE=0

# Run unit tests
echo "Step 1: Running unit tests..."
echo "----------------------------------------------------------------------"
bash run_unit_tests.sh
UNIT_TEST_EXIT=$?
if [ $UNIT_TEST_EXIT -ne 0 ]; then
    EXIT_CODE=1
fi

echo ""
echo ""

# Run notebook tests
echo "Step 2: Running notebook tests..."
echo "----------------------------------------------------------------------"
bash run_notebook_tests.sh
NOTEBOOK_TEST_EXIT=$?
if [ $NOTEBOOK_TEST_EXIT -ne 0 ]; then
    EXIT_CODE=1
fi

echo ""
echo "======================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "SUCCESS: All tests passed!"
else
    echo "FAILURE: Some tests failed."
    echo "  Unit tests: $([ $UNIT_TEST_EXIT -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
    echo "  Notebook tests: $([ $NOTEBOOK_TEST_EXIT -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
fi
echo "======================================================================"

exit $EXIT_CODE


